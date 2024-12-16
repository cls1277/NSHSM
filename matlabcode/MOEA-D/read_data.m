function bkg = read_data(path)
    fid = fopen(path, 'r');
    data = fscanf(fid, '%d');
    bkg = struct('factory', [], 'job', [], 'machine', [], 'operation', [], 'operations', [], 'machines', [], 'times', []);
    bkg.job = data(1);
    bkg.factory = data(2);
    bkg.machine = 5;
    bkg.operations = ones(bkg.job, 1) * 5;
    bkg.machines = cell(bkg.job, 1);
%     bkg.times = cell(bkg.job, 1);
    bkg.times = cell(bkg.factory, bkg.job);
    cnt = 3;
    for now_factory = 1:bkg.factory
        for now_job = 1:bkg.job
            cnt = cnt + 3;
            operations_m = cell(bkg.operations(now_job), 1);
            operations_t = cell(bkg.operations(now_job), 1);
            for operation = 1:5
                cnt = cnt + 2;
                nums = data(cnt);
                machines = zeros(1, nums);
                times = zeros(1, nums);
                for num = 1:nums
                    cnt = cnt + 1;
                    now_machine = data(cnt);
                    now_machine = now_machine - 1;
                    cnt = cnt + 1;
                    now_time = data(cnt);
                    machines(num) = now_machine;
                    times(num) = now_time;
                end
                operations_m{operation} = machines;
                operations_t{operation} = times;
            end
            if now_factory == 1
                bkg.machines{now_job} = [bkg.machines{now_job} operations_m];   
            end
            bkg.times{now_factory, now_job} = [bkg.times{now_factory, now_job} operations_t];
        end
    end
    bkg.operation = sum(bkg.operations);
end