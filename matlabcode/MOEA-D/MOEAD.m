classdef MOEAD < ALGORITHM
% <multi/many> <real/integer/label/binary/permutation>
% Multiobjective evolutionary algorithm based on decomposition
% type --- 1 --- The type of aggregation function

%------------------------------- Reference --------------------------------
% Q. Zhang and H. Li, MOEA/D: A multiobjective evolutionary algorithm based
% on decomposition, IEEE Transactions on Evolutionary Computation, 2007,
% 11(6): 712-731.
%------------------------------- Copyright --------------------------------
% Copyright (c) 2024 BIMK Group. You are free to use the PlatEMO for
% research purposes. All publications which use this platform or any code
% in the platform should acknowledge the use of "PlatEMO" and reference "Ye
% Tian, Ran Cheng, Xingyi Zhang, and Yaochu Jin, PlatEMO: A MATLAB platform
% for evolutionary multi-objective optimization [educational forum], IEEE
% Computational Intelligence Magazine, 2017, 12(4): 73-87".
%--------------------------------------------------------------------------

    methods
        function main(Algorithm,Problem)
            %% Parameter setting
            type = Algorithm.ParameterSet(1);

            %% DHFJSP
%             path = '10J2F';
%             path = ['C:/cls/cls1277/DHFJS/model-code/DHFJSP-benchmark/DQCE/' path '.txt'];
            path = Problem.getPath();
            global bkg;
            bkg = read_data(path);
            Problem = Problem.setParms(bkg);
            Problem.N = 100;
            [machines_, times_] = bkg2mat(bkg);
            randpt = initPop([Problem.N, bkg.factory, bkg.job], machines_', times_);
%             Population = Problem.Evaluation(randpt, bkg);
            Population = Problem.Evaluation(randpt, zeros(Problem.N, 1), bkg);

            %% Generate the weight vectors
            [W,Problem.N] = UniformPoint(Problem.N,Problem.M);
            T = ceil(Problem.N/10);

            %% Detect the neighbours of each solution
            B = pdist2(W,W);
            [~,B] = sort(B,2);
            B = B(:,1:T);

            %% Generate random population
            Z = min(Population.objs,[],'all');

            %% Optimization
            while Algorithm.NotTerminated(Population)
                Offsprings = [];
                % For each solution
                for i = 1 : Problem.N
                    % Choose the parents
                    P = B(i,randperm(size(B,2)));
                    % Generate an offspring
                    Offspring0 = OperatorGAhalf(Problem,Population(P(1:2)));

                    [pop_mat, ~] = pop2mat(Population(P(1:2)));
                    randpt = evolution([Problem.N, bkg.factory, bkg.job], machines_', times_, pop_mat');
                    Offspring2 = Problem.Evaluation(randpt(round(rand)+1,:), zeros(size(randpt,1), 1), bkg);
                    
                    Offsprings = [Offsprings, Offspring0, Offspring2];
                end
                [pop_mat, obj_mat] = pop2mat(Population);
                randpt = fullActive([Problem.N, bkg.factory, bkg.job], machines_', times_, pop_mat', obj_mat');
                Offspring1 = Problem.Evaluation(randpt, zeros(size(randpt, 1), 1), bkg);
                Offsprings = [Offsprings, Offspring1];
                Offsprings = removeDuplicatePopulation(Offsprings);
                Z = min(Z,min(Offsprings.objs,[],'all'));
                for Offspring = Offsprings
                    switch type
                        case 1
                            % PBI approach
                            normW   = sqrt(sum(W(P,:).^2,2));
                            normP   = sqrt(sum((Population(P).objs-repmat(Z,T,1)).^2,2));
                            normO   = sqrt(sum((Offspring.obj-Z).^2,2));
                            CosineP = sum((Population(P).objs-repmat(Z,T,1)).*W(P,:),2)./normW./normP;
                            CosineO = sum(repmat(Offspring.obj-Z,T,1).*W(P,:),2)./normW./normO;
                            g_old   = normP.*CosineP + 5*normP.*sqrt(1-CosineP.^2);
                            g_new   = normO.*CosineO + 5*normO.*sqrt(1-CosineO.^2);
                        case 2
                            % Tchebycheff approach
                            g_old = max(abs(Population(P).objs-repmat(Z,T,1)).*W(P,:),[],2);
                            g_new = max(repmat(abs(Offspring.obj-Z),T,1).*W(P,:),[],2);
                        case 3
                            % Tchebycheff approach with normalization
                            Zmax  = max(Population.objs,[],1);
                            g_old = max(abs(Population(P).objs-repmat(Z,T,1))./repmat(Zmax-Z,T,1).*W(P,:),[],2);
                            g_new = max(repmat(abs(Offspring.obj-Z)./(Zmax-Z),T,1).*W(P,:),[],2);
                        case 4
                            % Modified Tchebycheff approach
                            g_old = max(abs(Population(P).objs-repmat(Z,T,1))./W(P,:),[],2);
                            g_new = max(repmat(abs(Offspring.obj-Z),T,1)./W(P,:),[],2);
                    end
                    Population(P(g_old>=g_new)) = Offspring;
                end
            end
        end
    end
end