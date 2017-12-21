from flask import Flask,render_template,request,jsonify,g,make_response,send_from_directory,send_file
import sqlite3
import uuid
import time
import os

app = Flask(__name__)
DATABASE = 'paipai.db'

# 建立数据库连接
def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# 该装饰器使请求结束后自动调用该方法
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()

# 进入默认页面
@app.route("/")
def index():
    return render_template("index.html")

# 添加一个宝贝
@app.route("/addBaby",methods=["POST"])
def addBaby():
    conn = get_db()
    cu = conn.cursor()
    cu.execute("insert into paipai (id,babyName,babyUrl) values (?,?,?)",(str(uuid.uuid1()),request.form["babyName"],request.form["babyUrl"]))
    conn.commit()
    return jsonify()

# 加载所有宝贝
@app.route("/loadBabyList",methods=["GET"])
def loadBabyList():
    page = int(request.args["page"])# 当前页
    limit = int(request.args["limit"])# 每页个数
    kd = request.args.get("kd")# 关键字查询
    conn = get_db()
    cu = conn.cursor()
    #查询总数
    if kd :
        rs = cu.execute("select COUNT(*) from paipai where babyName like ? ",("%{:s}%".format(kd),))
    else:
        rs = cu.execute("select COUNT(*) from paipai")
    for row in rs:
        count = row[0]
    if count <= (page-1)*limit and page !=1:# 当最后一页只有一条的时候  点击删除  将查询上一页的数据
        page -= 1
    #查询结果集
    data = []
    if kd:
        rs = cu.execute("select id,babyName,babyUrl from paipai where babyName like ? limit ? offset ?", ("%{:s}%".format(kd),limit, (page - 1) * limit))
    else:
        rs = cu.execute("select id,babyName,babyUrl from paipai limit ? offset ?",(limit,(page-1)*limit))
    for row in rs:
        data.append({"id":row[0],"babyName":row[1],"babyUrl":row[2]})
    return jsonify({"code":0,"msg":"","count":count,"data":data})

# 删除宝贝
@app.route("/delBaby",methods=["POST"])
def delBaby():
    id = request.form["id"]
    conn = get_db()
    cu = conn.cursor()
    cu.execute("delete from paipai where id = ?",(id,))
    conn.commit()
    return jsonify()

# 导入数据  一个字典
@app.route("/importData",methods=["POST"])
def importData():
    file = eval(request.files["file"].read())# 转成字典
    if file:
        data = []
        for k,v in file.items():
            data.append((str(uuid.uuid1()),k,v))
        conn = get_db()
        cu = conn.cursor()
        cu.executemany("insert into paipai (id,babyName,babyUrl) values (?,?,?)",data)
        conn.commit()
    return jsonify({"code":0,"msg":"","data":{}})

# 下载数据 变成字典
@app.route("/exportData",methods=["GET"])
def exportData():
    conn = get_db()
    cu = conn.cursor()
    rs = cu.execute("select * from paipai")
    data = {}
    for row in rs:
        data[row[1]] = row[2]
    filename = "{}拍拍备份.json".format(time.strftime("%Y-%m-%d %H-%M-%S")).encode().decode('latin-1')# 中文文件名会报错
    response = make_response(str(data))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
    response.headers["Cache-Control"] = "public, max-age=0"
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response

@app.route("/reset")
def reset():
    # 在没有请求的情况下使用数据库不会自动销毁,所以加上一句话,就会自动销毁
    # with app.app_context():
    conn = get_db()
    cu = conn.cursor()
    cu.execute("drop table if exists paipai")
    cu.execute('''create table paipai
                   (id text primary key not null,
                   babyName text not null,
                   babyUrl text not null)''')
    return jsonify()

# 建表
# createTable()

# 服务启动 多线程
if __name__ == "__main__":
    app.run("127.0.0.1",80,debug=True,threaded=True)