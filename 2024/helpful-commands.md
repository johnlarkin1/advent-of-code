
**Showing directory structure:**
```shell
tree -I 'node_modules|__pycache__|scripts|debug|.o|deps|release|target'
```


**Getting core files**
```shell
files-to-prompt -e rs -e py -e toml --ignore "node_modules|__pycache__|scripts|debug|.o|deps|release|target|inputs" . | pbcopy
```
