import filecmp
  
f1 = "/home/kuo/gits/swervolf_scripts/registers.txt"
f2 = "/home/kuo/gits/swervolf_scripts/aes.txt"
  
# shallow comparison
result = filecmp.cmp(f1, f2)
print(result)
