function [machines_, times_] = bkg2mat(bkg)
    machines_ = zeros(bkg.job * 5, bkg.machine);
    times_ = zeros(bkg.machine, bkg.factory, bkg.job * 5);
    for i=1:bkg.job
        for j=1:5
            for l=bkg.machines{i,1}{j,1}
                machines_((i-1)*5+j, l+1) = 1;
            end
        end
    end

    for i=1:bkg.factory
        for j=1:bkg.job
            for k=1:5
                cnt = 0;
                for l=1:5
                    if machines_((j-1)*5+k, l)==1
                        cnt = cnt +1;
                        times_(l, i, (j-1)*5+k) = bkg.times{i,j}{k,1}(cnt);
                    end
                end
            end
        end
    end
end