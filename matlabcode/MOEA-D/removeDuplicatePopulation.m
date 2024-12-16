function uniquePopulation = removeDuplicatePopulation(Population)
    % 获取Population中obj的值
    objValues = cell2mat({Population.obj}');

    % 使用unique函数对obj的值进行去重
    [~, uniqueIndices, ~] = unique(objValues, 'rows');

    % 根据uniqueIndices提取不重复的Population条目
    uniquePopulation = Population(uniqueIndices);
end
