---
title: "St. Petersburg Paradox"
date: "2026-06-12"
disciplines: ["Mathematics", "Probability"] # Keep your existing taxonomy!
intro: "Imagine a game where a fair coin is tossed repeatedly until 'Heads' appears. If it appears on the 1st toss, you win €2. If it takes until the 2nd toss, you win €4. If it takes until the 3rd toss, you win €8, doubling every time."
question: "Mathematically speaking, what is the fair price you should be willing to pay to play this game just once if you want to break even?"
options: 
  - "Exactly €4"
  - "Roughly €20"
  - "Around €100"
  - "An infinite amount of money"
correct_answer: 4
hint: "To find the fair entry price, you need to calculate the expected value ($E$) of the game. Multiply the probability of each outcome by its corresponding prize value, and sum them all up for an infinite sequence of tosses."
explanation: "If you calculate the expected value ($E$) of the game using pure probability, the math looks like this: \n\n $$E = \\left(\\frac{1}{2} \\times 2\\right) + \\left(\\frac{1}{4} \\times 4\\right) + \\left(\\frac{1}{8} \\times 8\\right) + \\dots = 1 + 1 + 1 + \\dots = \\infty$$\n\nBecause the prize keeps doubling at the exact same rate that the probability of winning halves, the mathematical expectation is literally infinite. Therefore, from a purely theoretical standpoint, you should be willing to wager everything you own to play it just once.\n\n**The Paradox:** No sane person would actually pay more than a few euros to play this game. This happens because real-world casinos don't have infinite bankrolls to pay out if you flip a long streak of tails, and human beings naturally maximize *expected utility* (the psychological value of money) rather than pure expected financial value."
---