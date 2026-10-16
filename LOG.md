# Version 0 (Basic DPLL Solver):
*Started: 11.21.25 ==> Ended: 11.30.25*

### 11.22.25

Started setting up infrastructure of the code, mainly how expressions will form in CNF form. Literals, clauses, and expressions. Implementing DPLL after reading the literature, have to set up unit propagation.

### 11.26.25

Started implementing the DPLL algorithm. Implemented DIMACS-style variable names for literals

### 11.27.25

Made parsing work! Able to input a string and have it create and expression and sort it based on clause length.

### 11.30.25

SUCCESS! Version 0 is complete!! The SAT solver works on a variety of tests and is even faster then a few sites that I've seen. Theres a lot of room for improvement though, especially in terms of space allocation and backtracking. There is definitely a more elegant way to approach it, so I'm going to spend more time reading about other successful solvers and try to incorporate what they do into my own. I think I need to move on from the DPLL approach though. I'll also go talk to Daniel to see how their group were able to generate Costas Arrays and actually run their solver on it.

# Version 1 (2-Watched Literals Scheme + minor improvements)
*Started: 12.1.25 ==> Ended: 12.22.25*

### 12.1.25 - 12.12.25

Finals Week prep, didn't get much done

### 12.15.25 - 12.17.25

Did a lot of reading on SAT Solvers, particularly optimizations and how to start benchmarking my own sat solver with a .cnf format.

### 12.18.25

Implemented proper DIMACS file reading, specifically so that I can test my sat solver against the online .cnf files on the sat solver benchmark websites. With the # of variables and clauses given, we can move the unordered map into an array for much faster performance.

HUGE SPEED UP ALREADY!!

**_Testing uf250-01 from the benchmarks_**

1. Time to solve: 33.8272 seconds
2. Time to solve: 35.0956 seconds
3. Time to solve: 33.1517 seconds
   AVG: 34.025 seconds!

benchmarks/uf250-02.cnf --- Time to solve: ???? (DNF)

### 12.19.25

Did a lot more theory/reading work on Two-Watched literals. The concept of no work & O(1) being different was kind of interesting to think about. I think I've always assumed O(1) was "basically nothing" but basically nothing != nothing, which makes a lot of sense.

I'll need to implement a watchlist of some sort for every single clause thats in our expression. Maybe a task for tomorrow?

### 12.20.25

Improved the clause struct slightly by adding the basics of a watch list to it.

### 12.21.25

"Implemented" the two watched literals method (but need to test it and figure out what the bugs are...)

### 12.22.25

Fixed and implemented **a fully working two watched literals** method. Changed propagation method to queue based (BFS-style) rather than naive recursion. I also implemented a Clause-based heuristic that attacks smaller length clauses first.

This greatly improved performance on the initial test that I was using "uf250-01." The average time to compute this is now around 1-2 seconds, which is insane. It's making steady progress on the other "uf250-02" that it DNF'd before, but this still doesn't seem the best.

I think I need to play the optimization game some more, especially with this thing called "VSIDS" and CDCL. CDCL is the most viable next option, especially since it leads to less backtracking which is better for me.

# Version 2 (CDCL + messing with heuristics)
*Started 12.23.25 ==> Ended: ???*

### 12.23.25

VSIDS implementation was unsuccessful, but I spent a lot of time setting up the CDCL structure and backbone by going from trails as a vector of int to a vector of TrailEntry's. I also fixed some issues of duplicate propagates, which might have been the cause of the "hanging" that I was experiencing earlier. I'm really really happy with the current results---even though I haven't finished implementing full CDCL yet.

Current Benchmarks:

- CAN solve the sudoku.cnf file I got from (insert website), took 0.029 seconds
- uf250-01 ==> 0.003 seconds
- uf250-01 ==> 0.002

WOW! I need to make sure this isn't a bug though...

VERIFYING uf250-067:

- Time: ~0.002 seconds

My result: SAT v -1 2 3 -4 -5 -6 -7 8 9 10 -11 -12 14 15 16 -17 -18 -19 -20 22 -23 -24 25 -26 -27 -28 -29 30 -31 -32 -33 -34 -35 36 -37 38 -39 -41 42 43 -44 45 46 47 -48 -49 -50 51 -52 -53 -54 -55 -56 57 58 -59 -60 -61 62 -63 64 65 66 67 -68 -69 70 71 -72 73 -74 75 -76 -77 -78 79 80 -81 -83 84 -85 87 -88 89 90 91 92 -93 94 95 -96 97 -98 -99 100 -101 102 -103 -104 -105 106 107 -108 109 110 -111 -112 -113 -114 -115 -116 -117 -118 -119 120 -121 -122 -123 -124 -125 -126 -127 -128 129 130 -131 132 -133 -134 -135 -136 137 138 -139 -140 141 -142 -143 144 145 146 -147 -148 149 -150 151 -152 153 -154 155 -156 157 -158 159 -160 161 162 163 164 165 -166 -167 -168 -169 170 -171 172 173 -174 -175 -176 -177 -178 -179 -180 181 182 -183 -184 185 -186 -187 -188 -189 -190 191 192 -193 194 195 196 -197 -198 199 200 201 -202 -203 -204 -205 -206 207 -208 -209 210 -211 212 213 -214 215 216 217 218 -219 220 221 222 -223 -224 -225 226 -227 228 229 -230 -231 232 233 234 -235 236 -237 -238 239 -240 241 -242 -243 244 245 246 -247 248 249 250

Comparing with a working SAT solver:
**_"ERROR: Assignment does not satisfy expression!"_**

Upon further inspection (I added a verifier that plugs the values back in (should have done this a long time ago)), it seems that my SAT solver actually returns bogus values. So... the debugging continues

3.5 hours later, still debugging code that should be working...

I think I need to take a break from the code, go and read the theory again and write this from scratch again.

Deleting all the changes, reverting back to last commit.

### 12.30.25

Code refactoring + cleaning up

### 12.31.25

Working on CDCL + 1-UIP
Changing returns in propagate from T/F to -1 if true, else the conflicting clause index

ideally lock in for CDCL (??)
but midterms/stress from other stuff, i might take a pause on this for now

# Pause on Version 2, moving from working on a Solver to working on heuristics and learning other problems in the field

### 2.9.26

Started researching a bit into symmetry breaking / other optimizations in preprocessing.
I have an idea that might be helpful to generate variable heuristics --- so we'll see.

### 3.3.26
Switching up languages!! (DW——still english, pero quien sabe)

Using Python off of a recommendation from Vipin (goated) to use PySAT to experiment with my idea.

For now, generate a way to make CNFs for the Costas Array as a test example. And then use that to benchmark times with and without my idea.

### 3.4.26
Fully working CNF encoder for Costas Arrays! Also, I figured out how to use PySAT to both construct the cnf effectively and use minisat/cadical to solve it. Starting to work on trying out the heuristic idea!

### 3.6.26
Mr. Subercaseaux replied back to my email!! I'm super pumped to talk to him and get myself more involved within the field. (also grinding out the idea to make sure I can email him with something + maybe present something new?) 

### 3.7.26
Worked on the heatmap to visualize the performance of the heuristic. It doesn't seem to be working that well, particularly because the Costas Problem has so many solutions, so I might turn my attention to another problem. 

### 3.14.26
Spent a few hours learning about Golomb Rulers and their properties + construction methods.

### 3.16.26
I was bored in writing class and I was drawing marks on my paper when I realized that the sequence 2^i - 1 will always produce a Golomb Ruler (although not optimal) and that was pretty cool. I havent formally shown this to be true but it seems to be true from testing and it makes sense intuitively because of the uniquness of binary representation

### 3.22.26
Got an email back from Mr. Subercaseaux about perhaps working with him! (super excited about that) he also mentioned that he thought my ideas was pretty interesting, so I want to make sure I have something tangible to show him before we meet. 

...

### 5.11.26
It's been a shakey and rough couple of months, both with many academic and personal challenges, but summer has started and I want to take another shot at this. The small goal today is try to understand the workflow between Python and C code w/ MiniSAT to try to start automating the process before beginning to tweak the C code directly. Furhter, I also want to have something done to show Dr. Mackey and Mr. Subercaseaux by next week, so I'll be putting in more time this week to get this done soon.

FIRE okay I fixed the MiniSAT make and now I can use Python subprocess to encode, call minisat locally, and then print out all at once!

### 5.16.26
Cleaned up the code, but haven't modified MiniSAT yet

### 5.17.26
Spent extensive time studying how exactly MiniSAT works.

### 5.18.26 
***GREAT SUCCESS!!!!*** 

Modified MiniSAT to use a hardcoded scorecard that I got from the python generation function and it took a long long time to figure out how to fix the Makefile and other tiny linking bugs and I ended up adding a few functions and modifying the pickBranchLit function mainly and then ran it. 

INSANE! with fixed constants, the normal MiniSAT took around 30 seconds but now it takes around 3 seconds to solve the same problem! Really happy with this result, but I want to make sure that this isn't a fluke, so I'm going to make it more robust, bring in a control MiniSAT folder, and then present it to Dr. Mackey and Mr. Subercaseaux!

Started doing some code clean ups, and making a new "normal" MiniSAT! Can confirm it is not a fluke and we are saving >10 seconds. This can definitely be pushed further, but this is good enough concrete progress that I'm happy to email them about! 

I'm going to continue to tweak constants till I achieve a greater result.

AAAAAAAAND nevermind because I fully just inflated the time from the read/write i/o operations—if you use minisat not locally and with just pysat its so much faster and its not even a comparison ;-;

im trying to make it better and recover by using a bigger sized cnf but i think i see why there are specialized solvers.... learning this the hard way

### 5.19.26

I have finished with fixing as much as I can for now, and I realized that I don't need that many iterations to have a noticable impact on the heuristic!

```
NORMAL SOLVE TIME:                       8.483141333039384
HEURISTIC SOLVE TIME:                    5.629106416075956
└──> SPLIT:                              1.6016819160431623 + 4.027424500032794 
```

Given:
numIterations = 5
pctRandom = 93
trueWeightage = 5.5
falseWeightage = 1.5
GOLOMB_RULER_SIZE = 11
UPPER_L = 75

So I can finally go to sleep and count this as a W

### 5.20.26

Spent most of the day putting all of the work into a slideshow to share with Dr. Mackey, Mr. Subercaseaux, and Dr. Naik. This also served as a great benchmark of progress for me to consolidate all of my thoughts and work into one place. Added the slideshow to the project repo just for the sake of documentation as well.

I actually forgot to remake the modifiedMinisat, so using the same constants as above except with threshold as 7:

```
NORMAL SOLVE TIME:                       7.193725958000869
HEURISTIC SOLVE TIME:                    3.3133613319369033
└──> SPLIT:                              1.8338789159897715 + 1.4794824159471318 
```

FIRE! Thats like 1/2 of the time now and it improved by a lot more. I can definitely push this further, but I think this is good for now to send the slideshow and emails.

### 6.1.26

Met with Mr. Subercaseaux and he had a lot of valuable feedback. I'm really excited to continue working and learning from him. I'm going to try to see if I can come up with a better encoding for the Golomb Ruler and review the notes that I took during the meeting to see if I can implement any of the suggestions that he made as well as understand the "estimating asymptotic behavior if we used randomness" that he mentioned (the calculations to derive the n^4/(4L) upper bound)

### 6.3.26

Used a much better encoding for Golomb Ruler problem based on some suggestion from Mr. Subercaseaux. For order 11 we went from ~300k -> 30k for order 12 it was like 500k -> 50k. I think I'm going to use the order 13 with length 119 as the next test case as it takes usually ~16 seconds with normal minisat.

### 6.7.26 - 6.8.26
*wish i could have worked on this a lot more this week, but life and things got in the way*

- Running some basic tests with the new encoding and it seems to be working much better
- Found a bug with the old encoding
  - meant to compare the two, but during comparison I found a few bugs that caused encodingOne to return a bunch of bogus results, so I had to fix those before I could do a proper comparison
- Want to methodically test the new encoding so I wrote a simple `compare.py` to run a bunch of solving trials
  - also helps with visualizing how fixed order and decreasing length affects the solve time

### 6.14.26

- Finally fixed the bug w/ the modified minisat scorecard tracking
  - since I changed the encoding I had to update the `pickBranchLit_ScorecardHeuristic` function
- Added trace functionality, such that the current state of the ruler is written to a file
- Working on animation to play it back and visualize it
  - Saved traces folder + trace.py to visualize it -- rly good work done today i think

### 9.13.26

- Reorganized the repo to have a more clear structure and let future work happen more seamlessly

### 9.27.26

- Implementing an encoding & test for the crossing numbers to show viability of the heuristic on a different problem
- Dr. Mackey's star-parity relaxation is quite crazy, it is a much better encoding that a discrete geometry approach, and a lot more efficient than other encodings
   - I'm currently trying to see if I can use my heuristic on this to solve it faster than normal
- Current stats (testing on https://homes.cs.washington.edu/~kevinz/sat-solver/):
   - K6 took very little time to solve
   - K8 took ~1.7 seconds
   - K9 crashed the website LOL
   - K9 seems like a decent challenge then :)
- Worked on the K_8 case with at most 18 crossings (optimal) for testing
- Unfortunately it looks like this heuristic doesn't work well on this problem

Scorecard generation time: 0.035373666032683104 seconds
crossings (heuristic): 18

NORMAL SOLVE TIME:                       0.8106179999886081
HEURISTIC SOLVE TIME:                    9.682252208003774
└──> SPLIT:                              0.035373666032683104 + 9.646878541971091 

The heuristic makes it worse --- I suspect that this is because the crossing # 's encoding's solution space is not very correlated across relaxed subinstance solving, in comparison to the Golomb ruler/Costas array. I don't yet deeply understand the mathematics behind the encoding and output solution (e.g. "automorphisms" are still fuzzy for me), but perhaps in the future I can employ some symmetry breaking techniques or other tricks to make the output something more unique/correlated

### 10.1.26
Its my birthday today :)
- funnily enough found some errors and made the entire testing process easier by making the scorecard not hardcoded
- improved crossing #s testing a bit more so hopefully the chat with mackey goes good tmr!

### 10.2.26
- Found some critical issues with my benchmarking... 
   - I was not accounting for some overhead and when I standardized both tests: normal and heuristic solves, the heuristic was actually worse than the normal solve time for the golomb ruler problem which was pretty disheartening
- Fortunately, the talk with Dr. Mackey went well and he provided me some good feedback that I'll try integrating
- He also talked a lot more about Ramsey theory things, which I need to definitely learn a lot more about
- I'll also talk to Vipin + others to try to get a lot more data to hopefully tackle the Costas problem again
- Also from Mackey: *"dont put all your eggs in one basket"* 

### 10.15.26
- Went back to /vivsat_cpp and implemented the CDCL alg which I had previously paused on
    - Started to implement some stuff that will make CDCL easier later on (qhead + propagate params + return type)
- I'd like to eventually write my own SAT solver for the SAT 2027 comp, but we'll see how that goes :p



# TODO:
- Clean up repository again, make it a smoother workflow?
- Make a slideshow to show to Dr. Mackey/Mr. Subercaseaux?


# THINGS TO NOTE: 
- make golomb ruler animation have variable width for a sliding window animation
- think about "mapping" smaller golomb ruler solves to uknown lengths to improve the heuristic??
   - store a fixed database and run some precomps
   - same idea for a costas array, project smaller heatmaps to larger?

# TODO for `vivsat_cpp` 
- ~~DPLL Algorithm~~
- ~~DIMACS style input~~
- ~~Optimizations (Map --> Vector)~~
- ~~Two-watched literals~~
- ~~Queue-based propagation~~
- Clause learning (CDCL)
- VSIDS branching heuristic
- Restarts
- Shatter/symmetry breaking in preprocessing
- Memory layout optimizations
- Add a make file (c++ things, etc)

*Note: temporarily paused working on this to pursue other ideas. I feel as though I've understood enough of it myself - no point "reinventing the wheel" constantly, and rather maybe work on pushing the wheel further. :)*