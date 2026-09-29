import os

os.makedirs("data", exist_ok=True)

lenny_posts = {
    "Lennys_Newsletter_Growth_Loops.txt": """
# How to build a Growth Loop

A growth loop is a closed system where the inputs through some process generates more of an output that can be reinvested in the input. Traditional funnels operate in one direction: you put money in at the top (ads), and get users at the bottom. But loops are different.

## The Three Elements of a Loop
1. **Input:** A new user, or a specific action taken by an existing user.
2. **Action:** The step the user takes that creates value. (e.g., inviting a friend, creating public content).
3. **Output:** The result of the action, which brings in the next set of new users.

### Example: Pinterest's Content Loop
- **Input:** A user signs up.
- **Action:** They create a board and pin images. Pinterest's SEO automatically indexes this board.
- **Output:** A non-user searches Google for "wedding ideas", finds the Pinterest board, and signs up to view it. This new user becomes the input for the next loop.

To build a great product, you must transition from funnel-thinking to loop-thinking. Ask yourself: "How does one cohort of users directly lead to the next cohort of users?"
""",

    "Lennys_Newsletter_Finding_PMF.txt": """
# The Framework for Finding Product-Market Fit (PMF)

Product-Market Fit is the only thing that matters for an early-stage startup. But how do you know when you have it?

## The Superhuman Metric
Rahul Vohra popularized the "Sean Ellis test". Ask your users: "How would you feel if you could no longer use this product?"
If over 40% answer "Very Disappointed", you likely have PMF. 

## The Retention Plateau
The most objective measure of PMF is your retention curve. If you plot the percentage of users still active over time, it should eventually flatten out (a plateau) rather than dropping to zero. If it flattens above 20%, you have a solid business. 

## Signs you don't have PMF
1. Usage is growing, but only because you are spending massively on marketing.
2. Sales cycles are incredibly long, and customers don't renew.
3. Word of mouth is non-existent.

If you don't have PMF, do not scale your marketing. Focus entirely on talking to users, iterating the product, and narrowing your target audience until that retention curve flattens.
""",

    "Lennys_Newsletter_First_1000_Users.txt": """
# How the biggest consumer apps got their first 1,000 users

I spent the last month researching how companies like Airbnb, Uber, Tinder, and DoorDash acquired their initial user base. It turns out, almost none of them used paid ads. They did things that don't scale.

## 1. Go where your users are offline
- **Tinder:** Whitney Wolfe Herd visited college sororities, pitched the app, had everyone sign up on the spot, and then went to the fraternities to show them the app full of sorority girls. 
- **Uber:** Travis Kalanick went to the Caltrain station in San Francisco and handed out referral codes to tech workers arriving from the peninsula.

## 2. Piggyback off existing networks
- **Airbnb:** They built a bot to cross-post their listings to Craigslist. This gave them access to Craigslist's massive audience for free.

## 3. Create a viral waitlist
- **Robinhood:** Created a landing page promising zero-fee stock trading. When you signed up, you saw your place in line. You could jump ahead in line by referring friends. They got 1 million users before writing a line of code.

Focus on the micro. Do whatever it takes to get the first 10, 100, and 1,000 users manually.
""",

    "Lennys_Newsletter_B2B_Onboarding.txt": """
# Best practices for B2B SaaS Onboarding

Onboarding is the most critical phase of the customer journey. If a team doesn't reach the "Aha!" moment within their first week, they will likely churn within 90 days.

## 1. Time-to-Value (TTV)
Your primary goal is to minimize TTV. Map out every step a user must take to get value out of your product. Can you remove 30% of those steps? 

## 2. The Blank Slate Problem
Never drop a new user into an empty dashboard. Always provide templates, pre-filled dummy data, or an interactive tutorial. 
For example, when you join Notion, your workspace isn't empty—it's filled with "Getting Started" templates that teach you how the product works by using it.

## 3. Empty States as Call to Actions
If a user hasn't created a project yet, the "Projects" tab shouldn't just say "No projects". It should explain what a project is, why it's useful, and have a giant button saying "Create your first project".
""",

    "Lennys_Newsletter_Prioritization_Frameworks.txt": """
# The Ultimate Guide to Product Prioritization Frameworks

As a PM, you will always have more ideas than engineering capacity. Prioritization is your primary job. Here are the three most effective frameworks:

## 1. RICE Scoring
Developed by Intercom, RICE stands for:
- **Reach:** How many users will this impact in a given quarter?
- **Impact:** How much will this increase the primary metric? (3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal).
- **Confidence:** How confident are you in these estimates? (100% = high, 80% = medium, 50% = low).
- **Effort:** How many "person-months" will this take?

*Formula: (Reach * Impact * Confidence) / Effort*

## 2. The Kano Model
This maps features on two axes: Customer Satisfaction vs. Feature Implementation. It categorizes features into:
- **Basic Needs:** Things users expect (e.g., password reset). If missing, they are furious. If present, they are neutral.
- **Performance:** The more you have, the better (e.g., faster load times).
- **Delighters:** Unexpected features that create a "wow" moment.

## 3. Value vs. Complexity Matrix
A simple 2x2 grid. You map features based on Business Value (High/Low) and Implementation Complexity (High/Low).
- High Value / Low Complexity = Quick Wins (Do these first).
- High Value / High Complexity = Major Projects (Plan carefully).
- Low Value / Low Complexity = Fill-ins (Do when bored).
- Low Value / High Complexity = Time Sinks (Avoid).
""",

    "Lennys_Newsletter_Pricing_Strategies.txt": """
# SaaS Pricing Strategies: Freemium vs. Free Trial

Pricing is the most under-optimized lever in SaaS. Most founders guess their pricing instead of testing it. Let's break down the two dominant Go-To-Market motions.

## Freemium
You offer a robust free tier indefinitely, but lock advanced features or usage limits behind a paywall.
- **Pros:** Massive top-of-funnel growth. It acts as a marketing channel.
- **Cons:** You have to support a massive base of free users who cost you server money and support time but yield zero revenue.
- **When to use:** When your product has network effects (e.g., Slack, Zoom) or a massive total addressable market (e.g., Spotify).

## Free Trial
Users get access to the entire premium product for a limited time (usually 14 or 30 days), then must pay to continue.
- **Pros:** Urgency. Users know they have to evaluate it quickly. Higher conversion rates from those who actually try it.
- **Cons:** Lower top-of-funnel signups. 
- **When to use:** When your product solves a highly specific, acute B2B pain point (e.g., an enterprise CRM or a complex developer tool).

## Reverse Trial
A hybrid approach popularized by companies like Airtable. New users get a 14-day free trial of the *highest* premium tier. When the trial ends, they aren't kicked out; instead, they are downgraded to a basic Freemium tier. This gives them a taste of the best features, creating a strong desire to upgrade later.
""",

    "Lennys_Newsletter_Metrics_That_Matter.txt": """
# The 5 Growth Metrics That Actually Matter

Vanity metrics (like total registered users) will kill your company. You need to focus on actionable metrics.

## 1. Customer Acquisition Cost (CAC)
How much you spend on sales and marketing to acquire one paying customer. If you spend $10,000 on Google Ads and get 100 customers, your CAC is $100.

## 2. Lifetime Value (LTV)
The total gross margin you expect to make from a customer over their entire relationship with your company. 
Rule of thumb: Your LTV should be at least 3x your CAC.

## 3. CAC Payback Period
The time it takes for a customer to pay back the cost of acquiring them. For early-stage startups, this should be under 12 months. If it's longer, you will run out of cash trying to grow.

## 4. Net Revenue Retention (NRR)
This measures what happens to your revenue from a specific cohort of customers over time, including churn, downgrades, and upgrades (expansion revenue). 
An NRR over 100% means your company would still grow even if you never signed another new customer. Elite SaaS companies have NRR > 120%.

## 5. Daily Active Users / Monthly Active Users (DAU/MAU)
A measure of stickiness. If your DAU/MAU is 50%, it means the average user opens your app 15 days out of the month. WhatsApp has a DAU/MAU of over 85%. Most standard apps hover around 20%.
""",

    "Lennys_Newsletter_Hiring_PMs.txt": """
# How to Hire a Great Product Manager

Hiring a PM is arguably harder than hiring an engineer because the skills are highly subjective. Here is exactly what to look for:

## 1. High Agency
When things go wrong, do they blame the engineering team, the sales team, or the market? A high-agency PM says, "The timeline slipped, but here is what I am doing right now to unblock the team." They force outcomes into existence.

## 2. Extreme Clarity of Thought
PMs write specs, lead meetings, and align stakeholders. If their communication is messy, the product will be messy. In an interview, ask them to explain a complex hobby they have to a 5-year-old. If they can't simplify it, do not hire them.

## 3. Customer Obsession
A mediocre PM relies on market research reports. A great PM spends 30% of their week on Zoom calls with actual users. Ask them: "Tell me about the last time a user totally surprised you, and how it changed your roadmap."

## 4. The Take-Home Assignment
Do not ask them to "design an elevator for a 1,000-story building." That's useless. Give them a real, sanitized problem your company faced 6 months ago. Ask them to write a 1-page PRD (Product Requirements Document) outlining how they would solve it. Look for how they define success metrics.
"""
}

for filename, content in lenny_posts.items():
    with open(f"data/{filename}", "w", encoding="utf-8") as f:
        f.write(content.strip())

print("Lenny's expanded dataset generated successfully.")
