# A memo draft the reviewer caught (development run, 19 Oct 2026)

During development the writer (Claude Haiku 5.5) produced a first draft with this finding:

> "Past performance is a weak guide to future performance. For equity funds the best-performing quintile last year did
> slightly worse than the worst-performing quintile in the following year on average, and the gap is not statistically
> meaningful."

The reviewer flagged it: next-year excess return is −2.23 for the best quintile and −3.34 for the worst
(tab_persistence), so the best quintile did *better*, by 1.11 points. The draft went back to the writer once, and the
revised finding read:

> "Past one-year performance is a weak guide to the following year for equity funds: the best-performing fifth last
> year beat the worst-performing fifth by only about 1.1 points in the following year, and this gap is not
> statistically meaningful."

The Python check alone could not catch this: the draft had no number in that sentence, so there was nothing to compare
with a cell. Only the reading check could. That is why the memo goes through both.

In the same run the reviewer also raised two false alarms whose own reason said the finding was correct. The cause was
the order of the fields in the JSON Schema: the verdict came before the reason. With the reason first (current schema)
those false alarms disappeared, on the memo, on the paper write-ups and on the golden set.
