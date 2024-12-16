function [pop, obj] = pop2mat(Population)
    POPSIZE = size(Population, 2);
    D = size(Population(1).dec, 2);
    pop = zeros(POPSIZE, D);
    obj = zeros(POPSIZE, 2);
    for i=1:POPSIZE
        pop(i,:) = Population(1,i).dec;
        obj(i,:) = Population(1,i).obj;
    end
end