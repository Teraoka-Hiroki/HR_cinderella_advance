# 以下を「app.py」に書き込み
#token = "" # ご自身のトークンを入力
import streamlit as st
import numpy as np
import pandas as pd
import math
from base64 import b64encode
import amplify
from amplify import FixstarsClient
from amplify import solve, FixstarsClient
from amplify import Solver
import os
import networkx as nx
from io import StringIO



# タイトルの表示
st.title("ホームルーム シンデレラ（ADVANCE）")

# 説明の表示
st.write("「生徒のクラス分け」アプリ　FROM　量子アニーリングマシン：Fixstars Amplify")
#st.write("量子アニーリングマシン：Fixstars Amplify")

def make_groups(pairs):
    # ペアリストからグラフを生成
    G = nx.Graph()
    G.add_edges_from(pairs)

    # 連結成分（ここでは学生のグループ）を抽出
    groups = list(nx.connected_components(G))

    # 各グループをソート
    groups = [sorted(group) for group in groups]

    # 学生とその所属するグループの対応を表す辞書を作成
    student_to_group = {}
    for group in groups:
        for student in group:
            student_to_group[student] = group

    return groups, student_to_group


def can_assign(student, class_group, unwanted_pairs):
    for other_student in class_group:
        if (student, other_student) in unwanted_pairs or (other_student, student) in unwanted_pairs:
            return False
    return True


def assign_classes(groups, student_to_group, unwanted_pairs, num_classes=4):
    # クラスに生徒を割り当て
    classes = [set() for _ in range(num_classes)]  # クラスごとの生徒の集合を作成
    class_sizes = [0] * num_classes  # クラスのサイズ（生徒数）を追跡
    student_to_class = {}  # 生徒がどのクラスに割り当てられているかを追跡
    unassigned_students = set()  # 割り当てられなかった生徒を追跡

    for pair in unwanted_pairs:
        student1, student2 = pair

        # 各生徒に対して
        for student in [student1, student2]:
            # 生徒がすでにクラスに割り当てられている場合はスキップ
            if student in student_to_class:
                continue

            # 生徒が属しているグループを取得（グループがない場合は生徒自体がグループ）
            group = student_to_group.get(student, {student})

            # 生徒数が最小のクラスから順に、生徒をそのクラスに割り当てられるか確認
            for class_index in sorted(range(num_classes), key=lambda i: class_sizes[i]):
                if all(can_assign(s, classes[class_index], unwanted_pairs) for s in group):
                    # 生徒をクラスに割り当て
                    classes[class_index].update(group)
                    class_sizes[class_index] += len(group)
                    student_to_class.update({s: class_index for s in group})
                    break  # 割り当てに成功したら次の生徒へ
            else:
                # 全てのクラスで割り当てられない場合、生徒を未割り当てリストに追加
                unassigned_students.update(group)

    # 未割り当てのグループを割り当て
    unassigned_groups = [group for group in groups if not any(student in student_to_class for student in group)]
    for group in unassigned_groups:
        # 生徒数が最小のクラスから順に、生徒をそのクラスに割り当てられるか確認
        for class_index in sorted(range(num_classes), key=lambda i: class_sizes[i]):
            if all(can_assign(student, classes[class_index], unwanted_pairs) for student in group):
                # 生徒をクラスに割り当て
                classes[class_index].update(group)
                class_sizes[class_index] += len(group)
                student_to_class.update({s: class_index for s in group})
                break  # 割り当てに成功したら次のグループへ
        else:
            # 全てのクラスで割り当てられない場合、生徒を未割り当てリストに追加
            unassigned_students.update(group)

    return classes, unassigned_students


def save_results_to_csv(classes, num_students=100):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['出席番号'] + [f'{i} 組' for i in range(len(classes))])
    for i in range(1, num_students + 1):
        row = [i] + [1 if i in class_list else 0 for class_list in classes]
        writer.writerow(row)
    csv_content = output.getvalue()
    output.close()
    return csv_content

def pair_elements(original_list):
    result_list = []

    for sublist in original_list:
        for item in sublist[1:]:
            result_list.append([sublist[0], item])

    return result_list



def download_zip_file(zip_file_path, zip_file_name):
    with open(zip_file_path, "rb") as f:
        zip_file_bytes = f.read()
    st.download_button(
        label="Download ZIP File",
        data=zip_file_bytes,
        file_name=zip_file_name,
        mime="application/zip"
    )



def process_uploaded_file(file):
    df, column11_data, column12_data,column13_data,column14_data,column15_data,column16_data,column17_data,\
     column2_data, column3_data ,column4_data ,\
      column11_data_3to1,column12_data_3to1,column13_data_3to1,\
        column14_data_3to1,column15_data_3to1,column16_data_3to1,column17_data_3to1,\
          column11_data_5to1,column12_data_5to1,column13_data_5to1,\
            column14_data_5to1,column15_data_5to1,column16_data_5to1,column17_data_5to1,\
              column11_data_1to1,column12_data_1to1,column13_data_1to1,\
                column14_data_1to1,column15_data_1to1,column16_data_1to1,column17_data_1to1\
          = None, None, None, None, None, None,None,None,None,None, None, None, None, None, None, None, None, None,\
              None, None, None, None, None, None,None,None,None,None, None, None, None, None
          

    try:
        # CSVファイルを読み込む
        df = pd.read_csv(file)

        # 列ごとにデータをリストに格納
        column11_data = df.iloc[:, 2].tolist()
        # column11_dataの要素が5の場合は1にし、その他を0にするリストを作成する
        column11_data_5to1 = [1 if x == 5 else 0 for x in column11_data]
        column11_data_3to1 = [1 if x == 3 else 0 for x in column11_data]
        column11_data_1to1 = [1 if x == 1 else 0 for x in column11_data]

        column12_data = df.iloc[:, 3].tolist()
        column12_data_5to1 = [1 if x == 5 else 0 for x in column12_data]
        column12_data_3to1 = [1 if x == 3 else 0 for x in column12_data]
        column12_data_1to1 = [1 if x == 1 else 0 for x in column12_data]

        column13_data = df.iloc[:, 4].tolist()
        column13_data_5to1 = [1 if x == 5 else 0 for x in column13_data]
        column13_data_3to1 = [1 if x == 3 else 0 for x in column13_data]
        column13_data_1to1 = [1 if x == 1 else 0 for x in column13_data]

        column14_data = df.iloc[:, 5].tolist()
        column14_data_5to1 = [1 if x == 5 else 0 for x in column14_data]
        column14_data_3to1 = [1 if x == 3 else 0 for x in column14_data]
        column14_data_1to1 = [1 if x == 1 else 0 for x in column14_data]

        column15_data = df.iloc[:, 6].tolist()
        column15_data_5to1 = [1 if x == 5 else 0 for x in column15_data]
        column15_data_3to1 = [1 if x == 3 else 0 for x in column15_data]
        column15_data_1to1 = [1 if x == 1 else 0 for x in column15_data]

        column16_data = df.iloc[:, 7].tolist()
        column16_data_5to1 = [1 if x == 5 else 0 for x in column16_data]
        column16_data_3to1 = [1 if x == 3 else 0 for x in column16_data]
        column16_data_1to1 = [1 if x == 1 else 0 for x in column16_data]

        column17_data = df.iloc[:, 8].tolist()
        column17_data_5to1 = [1 if x == 5 else 0 for x in column17_data]
        column17_data_3to1 = [1 if x == 3 else 0 for x in column17_data]
        column17_data_1to1 = [1 if x == 1 else 0 for x in column17_data]

        column2_data  = df.iloc[:, 9].tolist()
        column3_data  = df.iloc[:, 10].tolist()
        
        if df.iloc[:, 11].tolist != None:
            column4_data  = df.iloc[:, 11].tolist()
        else:
           column4_data = None

    except Exception as e:
#        st.error(f"エラーが発生しました。: {e}")
        st.error(f"前のクラスが設定されていないファイルです。")
    return df, column11_data,column11_data_5to1,column11_data_1to1,\
                column12_data,column12_data_5to1,column12_data_1to1,\
                 column13_data,column13_data_5to1,column13_data_1to1,\
                  column14_data,column14_data_5to1,column14_data_1to1,\
                   column15_data,column15_data_5to1,column15_data_1to1,\
                    column16_data,column16_data_5to1,column16_data_1to1,\
                      column17_data,column17_data_5to1,column17_data_1to1,\
                        column2_data, column3_data, column4_data, \
                          column11_data_3to1, column12_data_3to1, column13_data_3to1,\
                            column14_data_3to1,column15_data_3to1,column16_data_3to1,column17_data_3to1

def upload_file_youin():
#    st.write("生徒の属性ファイルのアップロード")
    uploaded_file = st.file_uploader("生徒の属性のCSVファイルをアップロードしてください", type=["csv"])

    if uploaded_file is not None:
        # アップロードされたファイルを処理
        with st.spinner("ファイルを処理中..."):
#            df, column11_data,column12_data,column13_data,column14_data,column15_data,column16_data,column17_data, column2_data, column3_data, column4_data = process_uploaded_file(uploaded_file)
            df, column11_data,column11_data_5to1,column11_data_1to1,\
                column12_data,column12_data_5to1,column12_data_1to1,\
                 column13_data,column13_data_5to1,column13_data_1to1,\
                  column14_data,column14_data_5to1,column14_data_1to1,\
                   column15_data,column15_data_5to1,column15_data_1to1,\
                    column16_data,column16_data_5to1,column16_data_1to1,\
                      column17_data,column17_data_5to1,column17_data_1to1,\
                        column2_data, column3_data, column4_data,\
                          column11_data_3to1, column12_data_3to1, column13_data_3to1,\
                            column14_data_3to1,column15_data_3to1,column16_data_3to1,column17_data_3to1\
                              = process_uploaded_file(uploaded_file)

        # アップロードが成功しているか確認
        if df is not None:
            # アップロードされたCSVファイルの内容を表示
            st.write("アップロードされたCSVファイルの内容:")
            st.write(df)
            w11=column11_data
            w11_5to1 = column11_data_5to1
            w11_3to1 = column11_data_3to1
            w11_1to1 = column11_data_1to1

            w12=column12_data
            w12_5to1 = column12_data_5to1
            w12_3to1 = column12_data_3to1
            w12_1to1 = column12_data_1to1

            w13=column13_data
            w13_5to1 = column13_data_5to1
            w13_3to1 = column13_data_3to1
            w13_1to1 = column13_data_1to1

            w14=column14_data
            w14_5to1 = column14_data_5to1
            w14_3to1 = column14_data_3to1
            w14_1to1 = column14_data_1to1

            w15=column15_data
            w15_5to1 = column15_data_5to1
            w15_3to1 = column15_data_3to1
            w15_1to1 = column15_data_1to1

            w16=column16_data
            w16_5to1 = column16_data_5to1
            w16_3to1 = column16_data_3to1
            w16_1to1 = column16_data_1to1

            w17=column17_data
            w17_5to1 = column17_data_5to1
            w17_3to1 = column17_data_3to1
            w17_1to1 = column17_data_1to1

            w1=column2_data
            w2=column3_data
            if column4_data != None:
                p=column4_data
            else:
                p=None

            return w11, w11_5to1, w11_1to1, w12, w12_5to1, w12_1to1, w13, w13_5to1, w13_1to1, \
              w14, w14_5to1, w14_1to1, w15, w15_5to1, w15_1to1, w16, w16_5to1, w16_1to1, w17, w17_5to1, w17_1to1, w1, w2,p, \
                w11_3to1, w12_3to1, w13_3to1, w14_3to1, w15_3to1, w16_3to1, w17_3to1


def download_csv(data, filename='result_data.csv'):
    df = pd.DataFrame(data)
    csv = df.to_csv(index=True)

    b64 = b64encode(csv.encode()).decode()
    st.markdown(f'''
    <a href="data:file/csv;base64,{b64}" download="{filename}">
        クラス分け結果のダウンロード
    </a>
    ''', unsafe_allow_html=True)

def download_csv2(data, filename='pre_data.csv'):
    df = pd.DataFrame(data)
    csv = df.to_csv(index=True)

    b64 = b64encode(csv.encode()).decode()
    st.sidebar.markdown(f'''
    <a href="data:file/csv;base64,{b64}" download="{filename}">
        固定生徒ファイルのダウンロード
    </a>
    ''', unsafe_allow_html=True)


def left_column():
    st.sidebar.write("##固定する生徒のリストファイルの自動生成")
    st.sidebar.write("")


    selected_number=0
# プルダウンメニューで1から15までの整数を選択
    selected_number = st.sidebar.selectbox("クラス数を選んでください", list(range(0, 16)))
    if selected_number!=0:
        K = selected_number
        st.sidebar.write("クラス数：K = ",K)
    else:
        st.sidebar.write("クラス数を確定してください")

    number = st.sidebar.number_input("生徒数を入力してください", step=1)

    uploaded_file = st.sidebar.file_uploader("同じクラスにしたい生徒のリストファイルをアップロードしてください", type=['txt'])

    if uploaded_file is not None:
            content1 = uploaded_file.getvalue().decode("utf-8")
            token = content.strip()
            st.sidebar.success("リストを正常に読み込みました！")

    wanted_pairs = [content1.strip().split(',') for line in content1]
    wanted_pairs = pair_elements(wanted_pairs)

    uploaded_file2 = st.sidebar.file_uploader("違うクラスにしたい生徒のリストファイルをアップロードしてください", type=['txt'])

    if uploaded_file2 is not None:
            content2 = uploaded_file2.getvalue().decode("utf-8")
            token = content.strip()
            st.sidebar.success("リストを正常に読み込みました！")

    
    unwanted_pairs = [content2.strip().split(',') for line in content2]
    unwanted_pairs = pair_elements(unwanted_pairs)

    groups, student_to_group = make_groups(wanted_pairs)
    classes, unassigned_students = assign_classes(groups, student_to_group, unwanted_pairs, num_classes=K)

    st.sidebar.write(f"同じ組グループ: {groups}")
    st.sidebar.write(f"別の組グループ: {unwanted_pairs}")
    st.sidebar.write(f"未割り当ての生徒: {sorted(list(unassigned_students))}")

    df2 = save_results_to_csv(classes, num_students=number)

    st.sidebar.write(df2)

    st.sidebar.write("固定生徒のリストのCSVファイルをダウンロードしてください。")

    download_csv2(df2, filename='class_assignments_0.csv')

    # CSVファイルとしてダウンロードするためのリンクを生成
    #csv = df.to_csv(index=True)
    #b64 = base64.b64encode(csv.encode()).decode()
    #st.markdown(href, unsafe_allow_html=True)

left_column()

# Streamlitアプリの実行ファイル（app.py）と同じディレクトリにあるZIPファイルを指定
zip_file_name = "template_ADVANCE.zip"
zip_file_path = os.path.join(os.path.dirname(__file__), zip_file_name)

st.write("生徒の属性等のひな形をダウンロードしてください")

# ダウンロードボタンを表示
download_zip_file(zip_file_path, zip_file_name)

st.write("")

uploaded_file = st.file_uploader("トークンのテキストファイルをアップロードしてください", type=['txt'])

if uploaded_file is not None:
        content = uploaded_file.getvalue().decode("utf-8")
        token = content.strip()
        st.success("トークン文字列を正常に読み込みました！")


try:
        w11=None
#        w11, w12, w13, w14, w15,w16,w17,  w1, w2, p = upload_file_youin()
        w11, w11_5to1, w11_1to1, w12, w12_5to1, w12_1to1, w13, w13_5to1, w13_1to1, \
              w14, w14_5to1, w14_1to1, w15, w15_5to1, w15_1to1, w16, w16_5to1, w16_1to1, w17, w17_5to1, w17_1to1, w1, w2, p, \
                w11_3to1, w12_3to1, w13_3to1, w14_3to1, w15_3to1, w16_3to1, w17_3to1 = upload_file_youin()

        if p != None:
            before_class = 1
        else:
            before_class = 0

        # データフレームの値をNumpy
        N=len(w11)
        st.write("生徒数：N = ",N)

    # CSVファイルをアップロードする
        st.write("")
        uploaded_file = st.file_uploader("固定生徒のCSVファイルをアップロードしてください", type=['csv'])

        if uploaded_file is not None:
#            df = pd.read_csv(uploaded_file, header=None, skiprows=1, index_col=0)
            df = pd.read_csv(uploaded_file, header=None, skiprows=1, index_col=0, encoding='shift-jis')  # ここでエンコーディングを指定

        # データフレームの値をNumpy配列に変換
        values = df.values
        N1, K = values.shape
        # 決定変数の作成
        from amplify import BinarySymbolGenerator, BinaryPoly
        gen = BinarySymbolGenerator()  # 変数のジェネレータを宣言
        x = gen.array(N, K)  # 決定変数を作成

        # １の値のインデックスを取得し、ｘ[N,K]の配列に代入
        st.write("クラス数：K = ",K)
        for i in range(N):
            for j in range(K):
                if values[i, j] == 1:
                    x[i, j] = 1

        if before_class == 1:
            # Find the number of unique elements in the list
            num_unique = len(set(p))

            # Create a zero matrix of size (length of list, number of unique elements)
            one_hot = [[0 for _ in range(num_unique)] for _ in range(len(p))]

            # For each element in the list, set the corresponding element in the one-hot matrix to 1
            for i, element in enumerate(p):
                one_hot[i][element] = 1

            p=np.array(one_hot)
            # Print the one-hot matrix
#            st.write(p)


        lam1 = 10
        lam2 = 10

        a11=5
        a12=5
        a13=5
        a14=5
        a15=5
        a16=5
        a17=5

        b=5
        c=5
        d=1

        cost11  = 1/K * sum((sum(w11[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w11[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost12  = 1/K * sum((sum(w12[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w12[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost13  = 1/K * sum((sum(w13[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w13[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost14  = 1/K * sum((sum(w14[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w14[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost15  = 1/K * sum((sum(w15[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w15[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost16  = 1/K * sum((sum(w16[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w16[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost17  = 1/K * sum((sum(w17[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w17[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        
        cost11_5to1 = 1/K * sum((sum(w11_5to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w11_5to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost11_3to1 = 1/K * sum((sum(w11_3to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w11_3to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost11_1to1 = 1/K * sum((sum(w11_1to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w11_1to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        
        cost12_5to1 = 1/K * sum((sum(w12_5to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w12_5to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost12_3to1 = 1/K * sum((sum(w12_3to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w12_3to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))        
        cost12_1to1 = 1/K * sum((sum(w12_1to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w12_1to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))

        cost13_5to1 = 1/K * sum((sum(w13_5to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w13_5to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost13_3to1 = 1/K * sum((sum(w13_3to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w13_3to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))        
        cost13_1to1 = 1/K * sum((sum(w13_1to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w13_1to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))

        cost14_5to1 = 1/K * sum((sum(w14_5to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w14_5to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost14_3to1 = 1/K * sum((sum(w14_3to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w14_3to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))        
        cost14_1to1 = 1/K * sum((sum(w14_1to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w14_1to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))

        cost15_5to1 = 1/K * sum((sum(w15_5to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w15_5to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost15_3to1 = 1/K * sum((sum(w15_3to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w15_3to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))        
        cost15_1to1 = 1/K * sum((sum(w15_1to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w15_1to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))

        cost16_5to1 = 1/K * sum((sum(w16_5to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w16_5to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost16_3to1 = 1/K * sum((sum(w16_3to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w16_3to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))        
        cost16_1to1 = 1/K * sum((sum(w16_1to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w16_1to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))

        cost17_5to1 = 1/K * sum((sum(w17_5to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w17_5to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost17_3to1 = 1/K * sum((sum(w17_3to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w17_3to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))        
        cost17_1to1 = 1/K * sum((sum(w17_1to1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w17_1to1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        
        cost2 = 1/K * sum((sum(w1[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w1[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        cost3 = 1/K * sum((sum(w2[i]*x[i,k] for i in range(N)) - 1/K * sum(sum(w2[i]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
        
#        st.write(w11_5to1)

        if before_class == 1:

            cost4_0 = 1/K * sum((sum(p[i,0]*x[i,k] for i in range(N)) - 1/K * sum(sum(p[i,0]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
            cost4_1 = 1/K * sum((sum(p[i,1]*x[i,k] for i in range(N)) - 1/K * sum(sum(p[i,1]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
            cost4_2 = 1/K * sum((sum(p[i,2]*x[i,k] for i in range(N)) - 1/K * sum(sum(p[i,2]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))
            cost4_3 = 1/K * sum((sum(p[i,3]*x[i,k] for i in range(N)) - 1/K * sum(sum(p[i,3]*x[i,k] for i in range(N)) for k in range(K)))**2 for k in range(K))

            cost4 = cost4_0 + cost4_1 + cost4_2 + cost4_3

            cost = a11*cost11 + a12*cost12 + a13*cost13 + a14*cost14 + a15*cost15 + a16*cost16 + a17*cost17+ b*cost2 + c*cost3 +d*cost4\
              + a11*cost11_5to1 + a11*cost11_1to1 + a12*cost12_5to1 + a12*cost12_1to1 + a13*cost13_5to1 + a13*cost13_1to1 \
                + a14*cost14_5to1 + a14*cost14_1to1 + a15*cost15_5to1 + a15*cost15_1to1 + a16*cost16_5to1 + a16*cost16_1to1 + a17*cost17_5to1 + a17*cost17_1to1 \
                  + a11*cost11_3to1 + a12*cost12_3to1 + a13*cost13_3to1 + a14*cost14_3to1 \
                    + a15*cost15_3to1 + a16*cost16_3to1 + a17*cost17_3to1 

        else:
            cost = a11*cost11 + a12*cost12 + a13*cost13 + a14*cost14 + a15*cost15 + a16*cost16 + a17*cost17+ b*cost2 + c*cost3 \
              + a11*cost11_5to1 + a11*cost11_1to1 + a12*cost12_5to1 + a12*cost12_1to1 + a13*cost13_5to1 + a13*cost13_1to1 \
                + a14*cost14_5to1 + a14*cost14_1to1 + a15*cost15_5to1 + a15*cost15_1to1 + a16*cost16_5to1 + a16*cost16_1to1 + a17*cost17_5to1 + a17*cost17_1to1 \
                  + a11*cost11_3to1 + a12*cost12_3to1 + a13*cost13_3to1 + a14*cost14_3to1 \
                    + a15*cost15_3to1 + a16*cost16_3to1 + a17*cost17_3to1 
        
        penalty1 = lam1 * sum((sum(x[i,k] for k in range(K)) -1 )**2 for i in range(N))
        penalty2 = lam2 * sum((sum(x[i,k] for i in range(N)) -N/K )**2 for k in range(K))
        penalty = penalty1 + penalty2

        y = cost + penalty
        moku = y

            ##########
            # 求解
            ##########

            # 実行マシンクライアントの設定
        client = FixstarsClient()
        client.token = token
        client.parameters.timeout = 1 * 500  # タイムアウト0.5秒

            # アニーリングマシンの実行
        solver = Solver(client)  # ソルバーに使用するクライアントを設定
        result = solver.solve(moku)  # 問題を入力してマシンを実行

            # 解の存在の確認
        if len(result) == 0:
            raise RuntimeError("The given constraints are not satisfied")

            ################
            # 結果の取得
            ################
        values = result[0].values  # 解を格納
        x_solutions = x.decode(values)
        sample_array = x_solutions
        st.write("結果表示:")
        st.write(x_solutions)

        # ダウンロードボタンを表示
        download_csv(x_solutions)
        st.write('')
        st.write('')
        st.write('結果の確認')
        #生徒の成績テーブルの平均
        Wu11 = 1/K * sum(w11[i]*sum(sample_array[i][k] for k in range(K)) for i in range(N))
        st.write('成績1：'f'ave={Wu11}')
        Wu12 = 1/K * sum(w12[i]*sum(sample_array[i][k] for k in range(K)) for i in range(N))
        st.write('成績2：'f'ave={Wu12}')
        Wu13 = 1/K * sum(w13[i]*sum(sample_array[i][k] for k in range(K)) for i in range(N))
        st.write('成績3：'f'ave={Wu13}')
        Wu14 = 1/K * sum(w14[i]*sum(sample_array[i][k] for k in range(K)) for i in range(N))
        st.write('成績4：'f'ave={Wu14}')
        Wu15 = 1/K * sum(w15[i]*sum(sample_array[i][k] for k in range(K)) for i in range(N))
        st.write('成績5：'f'ave={Wu15}')
        Wu16 = 1/K * sum(w16[i]*sum(sample_array[i][k] for k in range(K)) for i in range(N))
        st.write('成績6：'f'ave={Wu16}')
        Wu17 = 1/K * sum(w17[i]*sum(sample_array[i][k] for k in range(K)) for i in range(N))
        st.write('成績7：'f'ave={Wu17}')

        W1u = 1/K * sum(w1[i]*sum(sample_array[i][k] for k in range(K)) for i in range(N))
        st.write('性別：'f'ave1={W1u}')
        W2u = 1/K * sum(w2[i]*sum(sample_array[i][k] for k in range(K)) for i in range(N))
        st.write('要支援：'f'ave2={W2u}')
        st.write('ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー')
        st.write('')
        #各クラスでの成績1合計、コスト（分散）、標準偏差を表示
        st.write('各クラスでの成績1合計、コスト（分散）、標準偏差を表示')
        cost = 0
        for k in range(K):
          value = 0
          for i in range(N):
            value = value + sample_array[i][k] * w11[i]
          st.write(f'{value=}')
          cost = cost + (value - Wu11)**2
        cost = 1/K * cost
        st.write(f'{cost=}')
        standard_deviation = math.sqrt(cost)#標準偏差
        st.write(f'{standard_deviation=}')
        st.write('')

        st.write('各クラスでの成績2合計、コスト（分散）、標準偏差を表示')
        cost = 0
        for k in range(K):
          value = 0
          for i in range(N):
            value = value + sample_array[i][k] * w12[i]
          st.write(f'{value=}')
          cost = cost + (value - Wu12)**2
        cost = 1/K * cost
        st.write(f'{cost=}')
        standard_deviation = math.sqrt(cost)#標準偏差
        st.write(f'{standard_deviation=}')
        st.write('')

        st.write('各クラスでの成績3合計、コスト（分散）、標準偏差を表示')
        cost = 0
        for k in range(K):
          value = 0
          for i in range(N):
            value = value + sample_array[i][k] * w13[i]
          st.write(f'{value=}')
          cost = cost + (value - Wu13)**2
        cost = 1/K * cost
        st.write(f'{cost=}')
        standard_deviation = math.sqrt(cost)#標準偏差
        st.write(f'{standard_deviation=}')
        st.write('')

        st.write('各クラスでの成績4合計、コスト（分散）、標準偏差を表示')
        cost = 0
        for k in range(K):
          value = 0
          for i in range(N):
            value = value + sample_array[i][k] * w14[i]
          st.write(f'{value=}')
          cost = cost + (value - Wu14)**2
        cost = 1/K * cost
        st.write(f'{cost=}')
        standard_deviation = math.sqrt(cost)#標準偏差
        st.write(f'{standard_deviation=}')
        st.write('')

        st.write('各クラスでの成績5合計、コスト（分散）、標準偏差を表示')
        cost = 0
        for k in range(K):
          value = 0
          for i in range(N):
            value = value + sample_array[i][k] * w15[i]
          st.write(f'{value=}')
          cost = cost + (value - Wu15)**2
        cost = 1/K * cost
        st.write(f'{cost=}')
        standard_deviation = math.sqrt(cost)#標準偏差
        st.write(f'{standard_deviation=}')
        st.write('')

        st.write('各クラスでの成績6合計、コスト（分散）、標準偏差を表示')
        cost = 0
        for k in range(K):
          value = 0
          for i in range(N):
            value = value + sample_array[i][k] * w16[i]
          st.write(f'{value=}')
          cost = cost + (value - Wu16)**2
        cost = 1/K * cost
        st.write(f'{cost=}')
        standard_deviation = math.sqrt(cost)#標準偏差
        st.write(f'{standard_deviation=}')
        st.write('')

        st.write('各クラスでの成績7合計、コスト（分散）、標準偏差を表示')
        cost = 0
        for k in range(K):
          value = 0
          for i in range(N):
            value = value + sample_array[i][k] * w17[i]
          st.write(f'{value=}')
          cost = cost + (value - Wu17)**2
        cost = 1/K * cost
        st.write(f'{cost=}')
        standard_deviation = math.sqrt(cost)#標準偏差
        st.write(f'{standard_deviation=}')
        st.write('')

        #各クラスに対して置くべき生徒を表示
        for k in range(K):
          st.write(f'{k=}', end=' : ')

          output_text = "    ".join([str(w17[i]) for i in range(N) if sample_array[i][k] == 1])
          st.write(output_text)
        st.write('')#改行
        st.write('ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー')
        #各クラスでの性別合計、コスト（分散）、標準偏差を表示
        st.write('各クラスでの性別合計、コスト（分散）、標準偏差を表示')
        cost1 = 0
        for k in range(K):
          value1 = 0
          for i in range(N):
            value1 = value1 + sample_array[i][k] * w1[i]
          st.write(f'{value1=}')
          cost1 = cost1 + (value1 - W1u)**2
        cost1 = 1/K * cost1
        st.write(f'{cost1=}')
        standard_deviation1 = math.sqrt(cost1)#標準偏差
        st.write(f'{standard_deviation1=}')
        st.write('')
        #各クラスに対して置くべき生徒を表示
#        for k in range(K):
#          st.write(f'{k=}', end=' : ')
#          output_text = "    ".join([str(w1[i]) for i in range(N) if sample_array[i][k] == 1])
#          st.write(output_text)
        st.write('')#改行
        st.write('ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー')
        #各クラスでの要支援合計、コスト（分散）、標準偏差を表示
        st.write('各クラスでの要支援合計、コスト（分散）、標準偏差を表示')
        cost2 = 0
        for k in range(K):
          value2 = 0
          for i in range(N):
            value2 = value2 + sample_array[i][k] * w2[i]
          st.write(f'{value2=}')
          cost2 = cost2 + (value2 - W2u)**2
        cost2 = 1/K * cost2
        st.write(f'{cost2=}')
        standard_deviation2 = math.sqrt(cost2)#標準偏差
        st.write(f'{standard_deviation2=}')
        st.write('')
        #各クラスに対して置くべき生徒を表示
#        for k in range(K):
#          st.write(f'{k=}', end=' : ')
#          output_text = "    ".join([str(w2[i]) for i in range(N) if sample_array[i][k] == 1])
#          st.write(output_text)
        st.write('')#改行
        st.write('ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー')

        #罰金項のチェック
        st.write('生徒一人のクラスの確認：count', end='')
        for i in range(N):
          count = 0
          for k in range(K):
              count = count + sample_array[i][k]
        output_text = "    ".join([str(count) for i in range(N)])
        st.write(output_text)

except Exception as e:
        st.error("ファイルアップロード後に計算されます".format(e))
#    st.error("ファイルアップロード後に計算されます{}".format(e))


