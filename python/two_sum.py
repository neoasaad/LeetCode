"""
Easy — Two Sum Hash Map
Time: O(n), Space: O(n)
Idea: For each num, check if target - num seen before.
"""
from typing import List
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        targets = {}
        for index, num in enumerate(nums):
            targets[target-num] = index
        for index, num in enumerate(nums):
            if num in targets and index != targets[num]:
                    return [index, targets[num]]
        return -1