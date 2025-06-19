# 打包命令
```python
pyinstaller --onefile --add-data "./draft_content_template.json:pyJianYingDraftMixed" jianying-draft-generator.py
```

# 可能遇到的问题

## uiautomation 兼容问题

```txt
ImportError: COM technology not available (maybe it's the wrong platform).
Note that COM is only supported on Windows.
```

### 解决方案
非 windows 不支持 uiautomation，需要移除 Jianying_controller

## 不支持的音频素材类型

pyJianYingDraft 使用了 libmediainfo 检测素材类型，有些发行版没有安装，导致素材检测失败

### 解决方案

```shell
$ sudo apt install libmediainfo-dev
```
## 不同平台剪映草稿配置文件名不一致

- windows: draft_content.json
- macOS: draft_info.json
