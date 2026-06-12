---
title: "Poisson Distribution"
date: "2026-06-12"
disciplines: ["Mathematics", "Probability"] # Keep your existing taxonomy!
intro: "Imagine you are looking at data for rare, independent events happening over time (like a specific machine component failing in a lab)."
question: "According to a classic Poisson distribution, if the average rate of this event is exactly **1 time per week**, what is the probability that a week passes with **zero** occurrences?"
options: 
- "Exactly 0%"
- "Roughly 18.4%"
- "Roughly 36.8%"
- "Exactly 50%"
correct_answer: 3
hint: "This is the ultimate trap for human intuition. When we hear an event happens '1 time per week on average,' our brains naturally assume a steady, linear distribution where every week gets exactly one event. But randomness doesn't like tidy schedules. Try using the core Poisson formula where the number of occurrences ($k$) is 0 and the average rate ($\\lambda$) is 1."
explanation: "To find the probability of exactly zero events occurring ($k = 0$) when the average rate ($\\lambda$) is 1, we plug the values into the Poisson probability mass function: \n\n$$P(k=0) = \\frac{\\lambda^k \\cdot e^{-\\lambda}}{k!} = \\frac{1^0 \\cdot e^{-1}}{0!} = \\frac{1}{e} \\approx 0.3678$$ \n\n This means that in any highly complex system running on random, independent variables (like server crashes, supply chain shocks, or market anomalies), you will face completely empty weeks nearly 37% of the time, while other weeks will inevitably cluster with multiple events simultaneously. Randomness is clumpier than our gut thinks it is!"

---