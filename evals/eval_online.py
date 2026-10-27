# online/triad_worker.py
import time
from dotenv import load_dotenv
from langsmith import Client

from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
)

load_dotenv()

PROJECT = "lenny-product-assistant"
JUDGE_MODEL = "gpt-4o-mini"
THRESHOLD = 0.7
SAMPLE_RATE = 1          # ~30% of traffic — 3 metrics × several calls each = expensive
POLL_SECONDS = 60

client = Client()


def _sampled(run):
    """Deterministic per-run sampling: same run always decided the same way."""
    return hash(str(run.id)) % 100 < SAMPLE_RATE * 100


def _existing_keys(run):
    """Which feedback keys this run already has — so we never re-judge a key."""
    fb = client.list_feedback(run_ids=[run.id])
    return {f.key for f in fb}


def score_recent_traces():
    """One pass: read recent RagPipeline traces, score any missing triad metric, push feedback."""
    runs = client.list_runs(
        project_name=PROJECT,
        is_root=True,             # RagPipeline root only, not child spans
        run_type="chain",
    )

    for run in runs:
        if not _sampled(run):
            continue

        outputs = run.outputs or {}
        answer = outputs.get("answer")
        context = outputs.get("context")     # post-rerank chunks — same field offline uses
        query = (run.inputs or {}).get("query", "")

        if not answer or not context:
            continue                          # nothing to judge

        already = _existing_keys(run)

        # each metric: (feedback key, metric object, which inputs it needs)
        # built fresh per run so scores/reasons don't leak between traces
        jobs = [
            ("faithfulness",
             FaithfulnessMetric(threshold=THRESHOLD, model=JUDGE_MODEL, include_reason=True),
             dict(input=query, actual_output=answer, retrieval_context=context)),

            ("answer_relevancy",
             AnswerRelevancyMetric(threshold=THRESHOLD, model=JUDGE_MODEL, include_reason=True),
             dict(input=query, actual_output=answer)),

            ("contextual_relevancy",
             ContextualRelevancyMetric(threshold=THRESHOLD, model=JUDGE_MODEL, include_reason=True),
             dict(input=query, actual_output=answer, retrieval_context=context)),
        ]

        metadata = run.extra.get("metadata", {}) if hasattr(run, "extra") and run.extra else {}
        user = metadata.get("user", "unknown")
        unscored_keys = [k for k, _, _ in jobs if k not in already]
        if unscored_keys:
            print(f"\n[Evaluating trace {str(run.id)[:8]}] user={user} | Q: '{query[:50]}'")

        for key, metric, tc_kwargs in jobs:
            if key in already:
                continue                      # per-key dedup: skip only what's already scored

            try:
                metric.measure(LLMTestCase(**tc_kwargs))
                client.create_feedback(
                    run_id=run.id,
                    key=key,
                    score=metric.score,
                    comment=metric.reason,
                )
                print(f"  -> {key}: {metric.score:.2f}")
            except Exception as e:
                # one metric failing shouldn't sink the other two for this trace
                print(f"  -> [{key}] failed on run {run.id}: {e}")


if __name__ == "__main__":
    import sys
    if "--once" in sys.argv:
        print("Running single evaluation pass on unscored traces...")
        score_recent_traces()
        print("\nAll unscored traces evaluated successfully!")
    else:
        while True:
            score_recent_traces()
            time.sleep(POLL_SECONDS)
