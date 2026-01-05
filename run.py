# backend_server/run.py
from app.app import app

if __name__ == '__main__':
    # host='0.0.0.0' 表示服务会在本机的所有网络IP上监听，方便局域网内其他设备访问
    # port=5000 是Flask默认端口，您可以根据需要修改
    app.run(host='0.0.0.0', port=5000, debug=True)
