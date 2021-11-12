import filecmp
  
f1 = "./golden.txt"
f2 = "./experiment.txt"
  
# shallow comparison
result = filecmp.cmp(f1, f2)
print(result)
