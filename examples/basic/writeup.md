# Task Four

For my task four implementation, I implemented a version of Steensgaard's algorithm for pointer
aliasing. I have managed to get it working in the sense that it does the pointer analyis, although
I have again run out of time to use it for implementing actual optimizations (more on that below).

To see that this is working, consider the results of running the following example (example.bril in the repo)
through steen.py via "bril2json < example.bril | python steen.py":

func1
p=p1	comp={'h1', 'a'}
p=p2	comp={'b', 'h2'}
p=p3	comp={'h3', 'c'}
p=q1	comp={'x', 'h4'}
p=q2	comp={'h5', 'y'}
p=q3	comp={'z', 'h6'}
p=a	comp={'h1', 'a'}
p=b	comp={'b', 'h2'}
p=c	comp={'h3', 'c'}
p=x	comp={'x', 'h4'}
p=y	comp={'h5', 'y'}
p=z	comp={'z', 'h6'}

func2
p=p1	comp={'x', 'h1', 'a', 'h4'}
p=p2	comp={'b', 'h2'}
p=p3	comp={'h3', 'c'}
p=q1	comp={'x', 'h1', 'a', 'h4'}
p=q2	comp={'h5', 'y'}
p=q3	comp={'z', 'h6'}
p=a	comp={'x', 'h1', 'a', 'h4'}
p=b	comp={'b', 'h2'}
p=c	comp={'h3', 'c'}
p=x	comp={'x', 'h1', 'a', 'h4'}
p=y	comp={'h5', 'y'}
p=z	comp={'z', 'h6'}

The only difference between func1 and func2 is that func2 stores the pointer a into
the location pointed to by the pointer q1. Since q1 points to the heap4 block,
these `points-to` equivalence classes have to be merged, which my implementation
seems to successfully handle. I used a union-find implementation found on the internet,
but otherwise the implementation was conceived by much trial-and-error searching through
the provided reference slides on the class git repo.

I had a lot of difficulty figuring out how to get the merge to properly work. In particular,
I didn't exactly comprehend the relation between the union-find and points-to relation as
it was vague (to me) in many of the slides. It made more sense once I understood the
reasoning behind the mysterious recursion here:

    def merge(x, y, uf, pts):
        x = uf[uf.find(x)]
        y = uf[uf.find(y)]
        if x == y: return
        uf.union(x, y)
        merge(pts[x], pts[y], uf, pts)

which of course turns out to be a simple tail-recursion whose purpose is to merge nested
chains of pointers.

# Catching up from previous missed tasks

A major reason I wasn't able to put this pointer analysis into action is that I spent
a significant amount of time catching up on work I have missed in the last two tasks.
I was a bit over optimistic about being able to implement a generic data-flow analysis
solver, with liveness, reaching, and constant propagation/folding all implemented,
as well as the pointer analysis and further optimizations. I learned a lot, and
had some success implementing the the previously described analyses which can be
found in mylive.py, reach.py, and cpf.py, respectively. I also implemented common
sub-expression elimination using local value numbering again without reference to
the implementation given in the repo, as I felt very uncertain that I had truly
grasped what was going on. I also rewrote my dead code elimination to use ud-chains
once I got the reaching analysis working.

The graphs results_less_than5000.png and results_over_5000.png show these particular results.
lvn is local value numbering (common sub-expression elimination) and cpf is constant folding
and constant propagation. both is when they are combined. (I should add for full transparency,
I used ChatGPT to make these figures by dumping in the output .csv file from brench)

Needless to say, I struggled on these assignments and have been humbled... Although I am
missing the main result here (which is using the pointer analysis to implement actual optimizations),
I hope that the implementation of Steensgaard's algorithm, as well as the more fleshed out
implementations of the other earlier non-loop optimizations from tasks one, and particularly tasks
two which I failed to turn in, provide some evidence that I was getting close to success on pointer
optimizations. I wanted to implement dead store elimination by referencing my dead code elimination
implementation that utilized reaching analysis, but didn't feel I had enough time tonight to
get a somewhat decent writeup along with figuring out the correct conversion between dead stores
and dead code (I assume it is relatively simple).
