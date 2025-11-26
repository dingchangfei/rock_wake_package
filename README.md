# Rock Wake - 耳机工作时的唤醒词监听工具

## 背景

这是一个为 macOS 设计的离线唤醒词监听工具。最初开发这个工具的动机是：**在戴着耳机工作时，经常听不到同事叫我，导致错过重要的沟通**。

通过使用 Picovoice 的 Porcupine 引擎，程序可以在后台持续监听指定的唤醒词。当检测到唤醒词时，会通过多种方式提醒你：
- 系统通知
- 系统提示音
- 语音提示
- 屏幕对话框
- 终端输出

这样即使戴着降噪耳机，也不会错过同事的呼唤。

## 功能特性

- **离线运行**：所有处理都在本地完成，无需网络连接，保护隐私
- **常驻运行**：程序持续运行，不会因为没有耳机就退出
- **智能检测**：根据耳机连接状态自动启用/暂停检测（可配置）
- **多种提醒**：通知、声音、语音、对话框多重保障
- **开机自启**：支持 LaunchAgent，开机自动启动

## 安装步骤

### 1. 安装依赖

```bash
# 安装 portaudio（pyaudio 需要）
brew install portaudio

# 安装 switchaudio-osx（可选，用于耳机检测）
brew install switchaudio-osx
```

### 2. 安装 Python 依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip3 install -r requirements.txt
```

### 3. 获取关键词文件

1. 访问 [Picovoice Console](https://console.picovoice.ai/)
2. 创建账户并获取 `ACCESS_KEY`
3. 创建自定义关键词（Custom Keyword）
4. 下载 `.ppn` 文件到项目根目录

### 4. 配置环境变量

```bash
export PV_ACCESS_KEY="你的AccessKey"
```

### 5. 准备模型文件（中文关键词需要）

如果使用中文关键词，需要下载中文模型文件：
1. 在 Picovoice Console 下载 `porcupine_params_zh.pv`
2. 放到项目根目录

## 配置说明

### 中文关键词（默认配置）

当前配置使用中文关键词，需要：

1. **关键词文件**：`.ppn` 文件（例如 `rock.ppn`）
2. **模型文件**：`porcupine_params_zh.pv`（中文模型）

配置文件位置：`listen_rock.py`

```python
KEYWORD_FILES = ["rock.ppn"]  # 你的中文关键词文件
MODEL_PATH = os.environ.get("PV_MODEL_PATH", "porcupine_params_zh.pv")  # 中文模型
```

### 英文关键词配置

如果要使用英文关键词，需要修改：

1. **修改关键词文件**：
   ```python
   KEYWORD_FILES = ["hey-computer.ppn"]  # 你的英文关键词文件
   ```

2. **移除或修改模型路径**：
   ```python
   # 方式1: 不指定模型路径（使用默认英文模型）
   MODEL_PATH = os.environ.get("PV_MODEL_PATH", None)
   
   # 方式2: 通过环境变量控制
   # export PV_MODEL_PATH=""  # 空值表示使用默认模型
   ```

3. **或者通过环境变量设置**：
   ```bash
   export PV_MODEL_PATH=""  # 空值使用默认英文模型
   python3 listen_rock.py --keywords hey-computer.ppn
   ```

**注意**：关键词文件（`.ppn`）和模型文件（`.pv`）的语言必须匹配：
- 中文关键词 → 中文模型（`porcupine_params_zh.pv`）
- 英文关键词 → 英文模型（默认，或 `porcupine_params.pv`）

## 运行方式

### 前台运行（测试用）

```bash
python3 listen_rock.py
```

### 后台运行方式

#### 方式1: LaunchAgent（推荐，开机自启）

```bash
# 安装并启动
./start_background.sh

# 停止
./stop_background.sh

# 查看状态
./check_status.sh

# 查看日志
tail -f /tmp/rockwake.out.log
tail -f /tmp/rockwake.err.log
```

#### 方式2: nohup（简单后台运行）

```bash
# 启动
./run_background.sh

# 查看日志
tail -f /tmp/rockwake_nohup.out
```

#### 方式3: 手动后台运行

```bash
# 使用 nohup
nohup python3 listen_rock.py > /tmp/rockwake.log 2>&1 &

# 使用 screen
screen -S rockwake
python3 listen_rock.py
# 按 Ctrl+A 然后 D 退出 screen，程序继续运行

# 重新连接
screen -r rockwake
```

## 高级配置

### 灵敏度调整

如果唤醒词检测不够灵敏，可以调整灵敏度：

```bash
# 使用命令行参数
python3 listen_rock.py --sensitivity 0.85

# 使用环境变量
export PV_SENSITIVITY=0.85
python3 listen_rock.py
```

**灵敏度说明**：
- 范围：0.0 - 1.0
- 默认值：0.8
- 越高越灵敏，但可能增加误报率
- 建议值：
  - 0.6-0.7：平衡模式（减少误报）
  - 0.75-0.8：灵敏模式（推荐）
  - 0.85-0.9：超灵敏模式（可能误报）

### 耳机检测配置

```bash
# 禁用耳机检测（始终激活）
python3 listen_rock.py --no-headphone-check

# 自定义检测间隔（秒）
python3 listen_rock.py --check-interval 3.0
```

## 程序特性

- **常驻运行**：程序会持续运行，不会因为没有耳机就退出
- **自动检测**：根据耳机连接状态自动启用/暂停检测
- **开机自启**：使用 LaunchAgent 方式可以在开机时自动启动
- **多重提醒**：通知、声音、语音、对话框确保不会错过

## 故障排查

### 通知不显示

检查系统设置：
- 系统设置 > 通知 > 终端（或 Python）> 允许通知
- 确保通知中心未被禁用
- 检查勿扰模式是否开启

### 检测不灵敏

1. 提高灵敏度：`--sensitivity 0.85`
2. 确保麦克风正常工作
3. 说话时声音清晰，语速适中
4. 减少环境噪音

### LaunchAgent 无法启动

1. 检查日志：`tail -f /tmp/rockwake.err.log`
2. 检查文件权限
3. 检查 Python 路径是否正确
4. 尝试使用 nohup 方式运行

## 许可证

本项目使用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！
