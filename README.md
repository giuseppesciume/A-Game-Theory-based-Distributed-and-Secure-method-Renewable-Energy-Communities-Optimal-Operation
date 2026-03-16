# A-Game-Theory-based-Distributed-and-Secure-method-Renewable-Energy-Communities-Optimal-Operation
A Game Theory based Distributed and Secure method Renewable Energy Communities Optimal Operation
In this work, a decentralized approach maximizing the above-listed objective functions is proposed, while preserving the privacy of end users. 
The proposed approach is resilient to possible failure of one or more units and do not rely on a central unit (single point of failure in centralized systems).

The proposed methodology is divided into two stages as indicated in the flow chart. 
The first stage is devoted to data acquisition, the second to the optimization of loads scheduling. 
As it will be proved, it allows reaching the maximum benefit without revealing any sensitive data.

Stage 1: initialization

All users are assigned a fixed number during the constitution of the REC and ordered from 1 to N. To make the process fairer, each time the algorithm is executed, a new random order is generated. In this way, although in each execution the random order may advantage who is selected first, in the longterm, due to the continuous mixing of the sequence, each participant has an equal opportunity to be in an advantageous position. Consequently, the advantage is distributed evenly over time. Therefore, in each execution, a temporary number is assigned to users. This temporary number determines the order in which the user exchanges data with others during a specific execution. For example, the user with the fixed number 1 might have, in a particular execution, the temporary number 3, meaning that it will be the third to exchange data.
At the end of this stage, the data that users need during stage 2 to perform optimization are acquired. The user having temporary number 1 is said “initiating” user. The overall REC’s hourly generation is sent to the “initiating” user from the generation plants that are in the REC. To compute the first objective function, in addition to the generation, which is a non-sensitive data, it is needed to know the sum of the consumptions of all users, which individually are sensitive data. To compute such a sum, in the proposed method, the Additive Secret Sharing (ASS) secure multiparty calculation technique is used [66]. Assuming that consumption does not vary too much over time, it is possible to approximate the user’s future consumption with the CBL. Thus, following the order established at the beginning:

1)	the “initiating” user extracts a vector of random numbers, adds them to its own CBL and sends the temporary sum to the next user;
2)	the latter adds its CBL to the temporary sum and passes it to the next user;
3)	the cycle goes on until the last user sends the temporary sum to the “initiating” user.

The temporary sum represents the total of all CBLs of all community members summed to a random number. At this point, Stage 2 can begin


Stage 2: optimization

Following the flow chart, the “initiating” user receives the total CBL of the community, subtracts the random numbers (which only he knows) from the temporary sum, and gets the total expected hourly consumption of the REC. In this way, the data needed for the optimization of OF1 are acquired, while ensuring privacy among users. 
As also the expected generation is known, the first optimization round can start. 
The result will be the choice of a consumption strategy for each individual user and thus the optimal allocation during the day of each user’s shiftable loads.
This choice is made through a multi-objective optimization of the functions defined.
The problem contains both continuous and binary variables, so a Multi-Objective Mixed-Integer Linear Programming (MO-MILP) method has been considered for the solution, using a weighted sum approach. 
The weighted-sum allows the trade-off between these two contrasting functions to be managed by weighting the importance of each objective.


The optimization procedure is designed as an iterative process that progressively converges toward an equilibrium point, resulting in a 24-hour vector expressed as in (7), which represents the consumption strategy for each user.

Initialization and first round

After Stage 1, starting from the "initiating" user, as shown by the flowchart in Fig. 1:
1.	each user adds their optimized consumption profile to the total baseline and forwards the updated value to the next user;
2.	the cycle continues until the last user sends to the "initiating" user the new total baseline, which consists of the sum of all the optimized users' consumption strategies;
3.	the "initiating" user performs a new optimization based on this updated total consumption. 


Second round and strategy update

During the second round, the "initiating" user evaluates whether to maintain or revise the strategy selected in the first round, assuming that the other users will not change their strategies.
The decision is made by checking whether the alternative strategy leads to:
-	a higher amount of energy sharing, thus increasing the user’s incentive gain; 
-	or an improvement in individual comfort, according to the weights assigned to the objective functions.
If the new strategy yields a better result, it replaces the previous one; otherwise, the previous strategy is maintained. 
The updated strategy is then added to the total consumption and transmitted to the next user, who performs the same evaluation. This is actually the search for a Nash-like equilibrium point, as the "initiating" user, as a result of the second optimization, may choose to change or not to change the strategy chosen during the first round. 


Convergence to equilibrium

At the end of the second round, the "initiating" user checks whether equilibrium has been reached. 
Equilibrium occurs when no user changes their strategy compared to the previous round.
Verification is performed by comparing the total baseline load CBLtot of the current round with that of the previous round:
-	if the two values differ, a new optimization round begins;
-	if they match, the process terminates, and equilibrium is achieved.

The convergence of the proposed iterative process is always guaranteed because, at each iteration, each user solves a deterministic mixed-integer linear optimization problem within a finite and bounded feasible space. 
The feasible space is bounded since all decision variables are limited by physical and operational constraints; in fact, each device can only be activated once per day (XS ∈[0, 1]), the total power consumption cannot exceed the user’s contracted capacity  (0 ≤ Pcj,h ≤ Px), and the scheduling horizon is finite (24 hours). 
At each iteration, a single user updates their load scheduling strategy while keeping the strategies of the others fixed.
Since each user has a finite and discrete set of possible actions, the process converges, in a finite number of steps, towards a steady-state configuration in which no participant can further improve their objective.
Such as it happens for Nash equilibrium, in this case the conditions for reaching convergence are listed below:
1.	Each user's sole goal is to maximize their own objective function.
2.	Each user chooses the best possible strategy, taking into account that the strategies chosen by all other users remain unchanged.
3.	Once equilibrium is reached, no single player can get a better result by changing their strategy alone, beyond the prescribed tolerance.
4.	Each user knows the rules of the game, the objective function structure, and the strategy that every other player is following.
5.	Every user knows that every other player is rational and satisfies all the above conditions.
6.	Players can choose their strategies independently. However, they must be able to deduce the optimal choices of others. 
These assumptions are satisfied in the proposed implementation, as confirmed by the experimental results discussed below.

Hence, the proposed approach allows multiple parties to work together to compute a common function needed to consider the behavior of all users, without having to reveal their data to others, while satisfying their own needs in a safe and efficient way.
In addition, the model is highly adaptable and flexible according to the available energy resources and the goals the REC wants to achieve. 
For example, in view of considering the REC as a new player in the power system able to provide energy services, such as DR, it is enough to add the request for power reduction or increase to OF1.

This method is not limited to offline execution based on pre-defined data, but can also be performed online.  In this case, consumption and generation profiles are updated progressively (e.g., every hour or every 15 minutes) and the sequential protocol allows each user to integrate their information in near real time. 
In this way, any dynamic changes in consumer behavior, such as the unexpected switching on of a device or lower than expected photovoltaic production, are automatically included in the next optimization cycle. 
The system is therefore able to adapt to changing conditions, converging towards a new allocation that reduces the distance from renewable generation and maximizes the shared benefit.


