# PoS_shuffle_grinding
Toy numeric simulation of proof-of-stake system, showing how a fair shuffle function can be gamed unfairly in the absence of safeguards.

We run two versions of the simulation:

+ In the first one, everybody plays nicely.
+ In the second one, Alice reserves one of her validators for triggering a shuffle re-roll when the first one does not go her way.

In a stronger version, Alice would reserve multiple validators for triggering rerolls.

In any case Alice is technically following the rules of the protocol. It could be debated whether this is an attack or just an underhanded technique. (It is not Alice’s fault if the protocol and incentive structure are arranged such that the game-theoretic optimal solution for an honest rational validator involves grinding)

This 'technique' can be prevented with timing safeguards.

`demo.py` output:
```
Running with 80 organic validators and 20 Alice validators
(Alice has 20.00% of the stake)
Without shuffle grinding, Alice won 20219 blocks out of 100000 (20.22%)
With shuffle grinding, Alice won 35251 blocks out of 100000 (35.25%)
```


