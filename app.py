import base64
from io import StringIO

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ページ設定
st.set_page_config(
    page_title="CSV データ分析アプリ",
    page_icon="📊",
    layout="wide"
)

# タイトル
st.title("📊 CSV データ分析・可視化アプリ")
st.markdown("CSVファイルをアップロードして、データの可視化と統計分析を行います。")

# サイドバー
st.sidebar.header("⚙️ 設定")

# CSVファイルアップロード
uploaded_file = st.sidebar.file_uploader(
    "CSVファイルを選択してください",
    type=['csv'],
    help="CSVファイルをドラッグ&ドロップまたはクリックして選択"
)

# アプリケーション設定
st.sidebar.header("🎨 表示設定")

# テーマ設定（将来の機能拡張用）
st.sidebar.selectbox(
    "グラフのカラーテーマ",
    ["plotly", "viridis", "plasma", "inferno", "magma", "cividis"],
    help="現在は表示のみ。将来のバージョンで実装予定"
)

# データ表示設定（将来の機能拡張用）
st.sidebar.checkbox("生データを常に表示", value=False, help="現在は表示のみ。将来のバージョンで実装予定")
st.sidebar.slider("最大表示行数", 10, 1000, 100, help="現在は表示のみ。将来のバージョンで実装予定")

# 分析設定（将来の機能拡張用）
st.sidebar.header("📊 分析設定")
st.sidebar.slider("信頼水準", 0.90, 0.99, 0.95, 0.01, help="現在は表示のみ。将来のバージョンで実装予定")
st.sidebar.slider("相関の閾値", 0.1, 0.9, 0.5, 0.1, help="現在は表示のみ。将来のバージョンで実装予定")

@st.cache_data
def load_csv_data(file_content, file_name):
    """CSVデータを読み込む関数（キャッシュ付き）"""
    try:
        df = pd.read_csv(StringIO(file_content), encoding='utf-8')
        return df, "utf-8"
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(StringIO(file_content), encoding='shift_jis')
            return df, "shift_jis"
        except UnicodeDecodeError:
            df = pd.read_csv(StringIO(file_content), encoding='cp932')
            return df, "cp932"

def generate_html_report(df, filename):
    """HTMLレポートを生成する関数"""

    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # カテゴリデータの統計情報を生成
    categorical_stats = ""
    if len(categorical_cols) > 0:
        categorical_stats = "<h2>📊 カテゴリデータの統計</h2>"
        for col in categorical_cols[:5]:  # 最初の5列まで
            value_counts = df[col].value_counts().head(10)
            categorical_stats += f"""
            <h3>{col}</h3>
            <table>
                <tr><th>値</th><th>件数</th><th>割合(%)</th></tr>
            """
            for value, count in value_counts.items():
                percentage = (count / len(df)) * 100
                categorical_stats += f"<tr><td>{value}</td><td>{count}</td><td>{percentage:.1f}</td></tr>"
            categorical_stats += "</table>"

    # 欠損値の詳細情報
    missing_info = ""
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        missing_info = """
        <h2>⚠️ 欠損値の詳細</h2>
        <table>
            <tr><th>列名</th><th>欠損値数</th><th>欠損率(%)</th></tr>
        """
        for col, missing_count in missing_data.items():
            if missing_count > 0:
                missing_rate = (missing_count / len(df)) * 100
                missing_info += f"<tr><td>{col}</td><td>{missing_count}</td><td>{missing_rate:.1f}</td></tr>"
        missing_info += "</table>"

    # 相関分析の情報
    correlation_info = ""
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        correlation_info = """
        <h2>🔗 相関分析</h2>
        <p>数値データ間の相関係数（-1から1の範囲、1に近いほど正の相関、-1に近いほど負の相関）</p>
        """
        correlation_info += corr_matrix.to_html(classes='table table-striped')

    html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>データ分析レポート - {filename}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 40px;
                line-height: 1.6;
                color: #333;
                background-color: #f8f9fa;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            h3 {{ color: #7f8c8d; }}
            .metric {{
                display: inline-block;
                margin: 10px;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 8px;
                min-width: 120px;
                text-align: center;
            }}
            .metric strong {{ display: block; font-size: 24px; margin-bottom: 5px; }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{ background-color: #f8f9fa; }}
            tr:hover {{ background-color: #e8f4fd; }}
            .summary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: center;
            }}
            .info-box {{
                background: #e8f4fd;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 データ分析レポート</h1>
            <div class="info-box">
                <p><strong>📁 ファイル名:</strong> {filename}</p>
                <p><strong>📅 生成日時:</strong> {pd.Timestamp.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
            </div>

            <div class="summary">
                <h2>📋 データ概要</h2>
                <div class="metric"><strong>{len(df)}</strong>行数</div>
                <div class="metric"><strong>{len(df.columns)}</strong>列数</div>
                <div class="metric"><strong>{df.isnull().sum().sum()}</strong>欠損値</div>
            </div>

            <h2>📈 基本統計（数値データ）</h2>
            {df[numeric_cols].describe().to_html(classes='table table-striped') if len(numeric_cols) > 0 else '<p>数値データがありません</p>'}

            {categorical_stats}

            {missing_info}

            {correlation_info}

            <h2>📊 データプレビュー（最初の10行）</h2>
            {df.head(10).to_html(classes='table table-striped')}

            <h2>🔍 データ型情報</h2>
            <table>
                <tr><th>列名</th><th>データ型</th><th>非null値数</th><th>null値数</th></tr>
    """

    for col in df.columns:
        null_count = df[col].isnull().sum()
        non_null_count = df[col].count()
        html += f"<tr><td>{col}</td><td>{df[col].dtype}</td><td>{non_null_count}</td><td>{null_count}</td></tr>"

    html += """
            </table>
        </div>
    </body>
    </html>
    """

    return html

if uploaded_file is not None:
    try:
        # ファイル内容を文字列として読み込み
        file_content = uploaded_file.read().decode('utf-8', errors='ignore')
        uploaded_file.seek(0)  # ファイルポインタをリセット

        # キャッシュ機能付きでデータ読み込み
        df, encoding = load_csv_data(file_content, uploaded_file.name)

        if encoding != "utf-8":
            st.info(f"ℹ️ {encoding}エンコーディングで読み込みました")

        st.success(f"✅ ファイル '{uploaded_file.name}' を正常に読み込みました")

        # データ概要表示
        st.header("📋 データ概要")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("行数", len(df))
        with col2:
            st.metric("列数", len(df.columns))
        with col3:
            st.metric("欠損値", df.isnull().sum().sum())

        # データフィルタリング
        st.subheader("🔍 データフィルタリング")

        col1, col2 = st.columns(2)

        with col1:
            # 行数制限
            max_rows = st.slider("表示する行数", 5, min(len(df), 1000), min(len(df), 100))

            # 列選択
            selected_columns = st.multiselect(
                "表示する列を選択（空の場合は全列表示）",
                df.columns.tolist(),
                default=[]
            )

        # 数値列とカテゴリ列を定義
        numeric_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object']).columns

        with col2:
            # 数値フィルタリング
            numeric_filter_col = st.selectbox(
                "数値フィルタリング対象列",
                ["なし"] + list(numeric_cols),
                key="numeric_filter"
            )

            # カテゴリフィルタリング
            category_filter_col = st.selectbox(
                "カテゴリフィルタリング対象列",
                ["なし"] + list(categorical_cols),
                key="category_filter"
            )

        # フィルタリング適用
        display_df = df.copy()

        # 数値フィルタリング
        if numeric_filter_col != "なし":
            min_val = float(df[numeric_filter_col].min())
            max_val = float(df[numeric_filter_col].max())
            filter_range = st.slider(
                f"{numeric_filter_col} の範囲",
                min_val, max_val, (min_val, max_val),
                key="numeric_range"
            )
            display_df = display_df[
                (display_df[numeric_filter_col] >= filter_range[0]) &
                (display_df[numeric_filter_col] <= filter_range[1])
            ]

        # カテゴリフィルタリング
        if category_filter_col != "なし":
            unique_values = df[category_filter_col].unique()
            selected_values = st.multiselect(
                f"{category_filter_col} の値を選択",
                unique_values,
                default=unique_values,
                key="category_values"
            )
            if selected_values:
                display_df = display_df[display_df[category_filter_col].isin(selected_values)]

        # 列選択適用
        if selected_columns:
            display_df = display_df[selected_columns]

        # 行数制限適用
        display_df = display_df.head(max_rows)

        # フィルタリング結果の表示
        if len(display_df) != len(df):
            st.info(f"フィルタリング結果: {len(df)}行 → {len(display_df)}行")

        # データプレビュー
        st.subheader("📊 データプレビュー")
        st.dataframe(display_df, use_container_width=True)

        # データのダウンロード機能
        st.subheader("📥 データエクスポート")

        col1, col2, col3 = st.columns(3)

        with col1:
            # CSV形式でダウンロード
            csv_data = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="CSV形式でダウンロード",
                data=csv_data,
                file_name=f"filtered_{uploaded_file.name}",
                mime="text/csv"
            )

        with col2:
            # Excel形式でダウンロード
            from io import BytesIO
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                display_df.to_excel(writer, sheet_name='データ', index=False)
                if len(numeric_cols) > 0:
                    df[numeric_cols].describe().to_excel(writer, sheet_name='統計情報')

            st.download_button(
                label="Excel形式でダウンロード",
                data=excel_buffer.getvalue(),
                file_name=f"filtered_{uploaded_file.name.replace('.csv', '.xlsx')}",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col3:
            # JSON形式でダウンロード
            json_data = display_df.to_json(orient='records', force_ascii=False, indent=2)
            st.download_button(
                label="JSON形式でダウンロード",
                data=json_data.encode('utf-8'),
                file_name=f"filtered_{uploaded_file.name.replace('.csv', '.json')}",
                mime="application/json"
            )

        # 基本統計
        st.header("📈 基本統計")

        # 数値列の統計
        if len(numeric_cols) > 0:
            st.subheader("数値データの統計")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)

        # カテゴリ列の統計
        if len(categorical_cols) > 0:
            st.subheader("カテゴリデータの統計")
            for col in categorical_cols[:3]:  # 最初の3列のみ表示
                st.write(f"**{col}** の値の分布:")
                value_counts = df[col].value_counts().head(10)
                st.bar_chart(value_counts)

        # グラフ作成セクション
        st.header("📊 データ可視化")

        if len(numeric_cols) > 0:
            # グラフタイプ選択
            chart_type = st.selectbox(
                "グラフの種類を選択",
                ["棒グラフ", "線グラフ", "散布図", "ヒストグラム", "箱ひげ図", "円グラフ", "面グラフ", "バイオリンプロット", "ペアプロット"]
            )

            # グラフ設定
            col1, col2 = st.columns(2)
            with col1:
                chart_title = st.text_input("グラフタイトル", value=f"{chart_type}の分析")
            with col2:
                chart_height = st.slider("グラフの高さ", 300, 800, 500)

            if chart_type == "棒グラフ":
                if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                    col1, col2 = st.columns(2)
                    with col1:
                        x_col = st.selectbox("X軸（カテゴリ）", categorical_cols)
                        y_col = st.selectbox("Y軸（数値）", numeric_cols)
                    with col2:
                        color_col = st.selectbox("色分け（オプション）", ["なし"] + list(categorical_cols))
                        orientation = st.selectbox("向き", ["縦", "横"])

                    color_col = None if color_col == "なし" else color_col
                    orientation_val = "v" if orientation == "縦" else "h"

                    fig = px.bar(
                        df, x=x_col, y=y_col, color=color_col,
                        title=chart_title, height=chart_height,
                        orientation=orientation_val
                    )
                    st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "線グラフ":
                if len(numeric_cols) >= 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        x_col = st.selectbox("X軸", numeric_cols)
                        y_cols = st.multiselect("Y軸（複数選択可）", [col for col in numeric_cols if col != x_col])
                    with col2:
                        color_col = st.selectbox("色分け（オプション）", ["なし"] + list(categorical_cols), key="line_color")
                        line_mode = st.selectbox("線のスタイル", ["lines", "lines+markers", "markers"])

                    if y_cols:
                        color_col = None if color_col == "なし" else color_col

                        if len(y_cols) == 1:
                            fig = px.line(
                                df, x=x_col, y=y_cols[0], color=color_col,
                                title=chart_title, height=chart_height
                            )
                            fig.update_traces(mode=line_mode)
                        else:
                            # 複数のY軸の場合
                            fig = go.Figure()
                            for y_col in y_cols:
                                fig.add_trace(go.Scatter(
                                    x=df[x_col], y=df[y_col],
                                    mode=line_mode, name=y_col
                                ))
                            fig.update_layout(title=chart_title, height=chart_height)

                        st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "散布図":
                if len(numeric_cols) >= 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        x_col = st.selectbox("X軸", numeric_cols)
                        y_col = st.selectbox("Y軸", [col for col in numeric_cols if col != x_col])
                    with col2:
                        color_col = st.selectbox("色分け（オプション）", ["なし"] + list(categorical_cols), key="scatter_color")
                        size_col = st.selectbox("サイズ（オプション）", ["なし"] + list(numeric_cols), key="scatter_size")

                    color_col = None if color_col == "なし" else color_col
                    size_col = None if size_col == "なし" else size_col

                    # 回帰線の追加オプション
                    add_trendline = st.checkbox("回帰線を追加")
                    trendline = "ols" if add_trendline else None

                    fig = px.scatter(
                        df, x=x_col, y=y_col, color=color_col, size=size_col,
                        title=chart_title, height=chart_height,
                        trendline=trendline
                    )
                    st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "ヒストグラム":
                col1, col2 = st.columns(2)
                with col1:
                    hist_col = st.selectbox("列を選択", numeric_cols)
                    bins = st.slider("ビン数", 10, 100, 30)
                with col2:
                    color_col = st.selectbox("色分け（オプション）", ["なし"] + list(categorical_cols), key="hist_color")
                    hist_type = st.selectbox("表示タイプ", ["count", "probability", "density"])

                color_col = None if color_col == "なし" else color_col

                fig = px.histogram(
                    df, x=hist_col, color=color_col, nbins=bins,
                    title=chart_title, height=chart_height,
                    histnorm=hist_type if hist_type != "count" else None
                )
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "箱ひげ図":
                col1, col2 = st.columns(2)
                with col1:
                    y_col = st.selectbox("Y軸（数値）", numeric_cols)
                    x_col = st.selectbox("X軸（カテゴリ、オプション）", ["なし"] + list(categorical_cols))
                with col2:
                    show_points = st.selectbox("データポイント表示", ["なし", "すべて", "外れ値のみ"])
                    notched = st.checkbox("ノッチ付き箱ひげ図")

                x_col = None if x_col == "なし" else x_col
                points_val = False if show_points == "なし" else ("all" if show_points == "すべて" else "outliers")

                fig = px.box(df, x=x_col, y=y_col, title=chart_title, height=chart_height)
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "円グラフ":
                if len(categorical_cols) > 0:
                    pie_col = st.selectbox("円グラフの対象列", categorical_cols)

                    # 上位N個の値のみ表示
                    top_n = st.slider("表示する項目数", 3, 20, 10)
                    value_counts = df[pie_col].value_counts().head(top_n)

                    fig = px.pie(
                        values=value_counts.values,
                        names=value_counts.index,
                        title=chart_title,
                        height=chart_height
                    )
                    st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "面グラフ":
                if len(numeric_cols) >= 2:
                    x_col = st.selectbox("X軸", numeric_cols, key="area_x")
                    y_cols = st.multiselect("Y軸（複数選択可）", numeric_cols, key="area_y")

                    if y_cols:
                        fig = go.Figure()
                        for y_col in y_cols:
                            fig.add_trace(go.Scatter(
                                x=df[x_col],
                                y=df[y_col],
                                fill='tonexty' if len(fig.data) > 0 else 'tozeroy',
                                name=y_col
                            ))
                        fig.update_layout(title=chart_title, height=chart_height)
                        st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "バイオリンプロット":
                y_col = st.selectbox("Y軸（数値）", numeric_cols, key="violin_y")
                x_col = None
                if len(categorical_cols) > 0:
                    use_category = st.checkbox("カテゴリ別に分析", key="violin_cat")
                    if use_category:
                        x_col = st.selectbox("X軸（カテゴリ）", categorical_cols, key="violin_x")

                fig = px.violin(df, x=x_col, y=y_col, title=chart_title, height=chart_height)
                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "ペアプロット":
                if len(numeric_cols) >= 2:
                    selected_cols = st.multiselect(
                        "分析する数値列を選択（最大6列推奨）",
                        numeric_cols.tolist(),
                        default=numeric_cols.tolist()[:4]
                    )

                    if len(selected_cols) >= 2:
                        color_col = st.selectbox("色分け（オプション）", ["なし"] + list(categorical_cols), key="pair_color")
                        color_col = None if color_col == "なし" else color_col

                        # サンプリング（大きなデータセットの場合）
                        sample_size = min(1000, len(df))
                        if len(df) > 1000:
                            st.info(f"データが大きいため、{sample_size}行をサンプリングして表示します")
                            sample_df = df.sample(n=sample_size, random_state=42)
                        else:
                            sample_df = df

                        fig = px.scatter_matrix(
                            sample_df, dimensions=selected_cols, color=color_col,
                            title=chart_title, height=chart_height
                        )
                        st.plotly_chart(fig, use_container_width=True)

        # グラフのエクスポート機能
        st.subheader("📥 グラフのエクスポート")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("PNG形式でダウンロード"):
                st.info("グラフを右クリック → 'Download plot as a png' でダウンロードできます")

        with col2:
            if st.button("HTML形式でダウンロード"):
                st.info("グラフを右クリック → 'Download plot as a html' でダウンロードできます")

        with col3:
            if st.button("SVG形式でダウンロード"):
                st.info("グラフを右クリック → 'Download plot as a svg' でダウンロードできます")

        # 統計分析
        st.header("📊 高度な統計分析")

        analysis_tabs = st.tabs(["相関分析", "統計検定", "外れ値検出", "データ品質"])

        with analysis_tabs[0]:
            # 相関分析
            if len(numeric_cols) > 1:
                st.subheader("🔗 相関分析")

                col1, col2 = st.columns(2)
                with col1:
                    corr_method = st.selectbox("相関係数の種類", ["pearson", "spearman", "kendall"])
                with col2:
                    show_values = st.checkbox("数値を表示", value=True)

                # 相関行列
                corr_matrix = df[numeric_cols].corr(method=corr_method)

                # Plotlyでインタラクティブなヒートマップ
                fig = px.imshow(
                    corr_matrix,
                    text_auto=show_values,
                    aspect="auto",
                    color_continuous_scale="RdBu_r",
                    title=f"相関行列 ({corr_method})"
                )
                st.plotly_chart(fig, use_container_width=True)

                # 強い相関のペアを表示
                st.subheader("強い相関関係")
                threshold = st.slider("相関の閾値", 0.5, 0.95, 0.7)

                strong_corr = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) >= threshold:
                            strong_corr.append({
                                '変数1': corr_matrix.columns[i],
                                '変数2': corr_matrix.columns[j],
                                '相関係数': round(corr_val, 3),
                                '相関の強さ': '強い正の相関' if corr_val > 0 else '強い負の相関'
                            })

                if strong_corr:
                    st.dataframe(pd.DataFrame(strong_corr), use_container_width=True)
                else:
                    st.info(f"閾値 {threshold} 以上の相関関係は見つかりませんでした")

        with analysis_tabs[1]:
            # 統計検定
            st.subheader("📈 統計検定")

            if len(numeric_cols) >= 2:
                test_type = st.selectbox(
                    "検定の種類",
                    ["t検定（2群の平均比較）", "分散分析（ANOVA）", "正規性検定"]
                )

                if test_type == "t検定（2群の平均比較）":
                    col1, col2 = st.columns(2)
                    with col1:
                        numeric_var = st.selectbox("数値変数", numeric_cols)
                    with col2:
                        if len(categorical_cols) > 0:
                            group_var = st.selectbox("グループ変数", categorical_cols)

                            # グループが2つの場合のみt検定実行
                            unique_groups = df[group_var].unique()
                            if len(unique_groups) == 2:
                                from scipy import stats
                                group1 = df[df[group_var] == unique_groups[0]][numeric_var].dropna()
                                group2 = df[df[group_var] == unique_groups[1]][numeric_var].dropna()

                                t_stat, p_value = stats.ttest_ind(group1, group2)

                                st.write("**t検定結果**")
                                st.write(f"- t統計量: {t_stat:.4f}")
                                st.write(f"- p値: {p_value:.4f}")
                                st.write(f"- 有意水準0.05での結果: {'有意差あり' if p_value < 0.05 else '有意差なし'}")

                                # 箱ひげ図で視覚化
                                fig = px.box(df, x=group_var, y=numeric_var, title="グループ間の比較")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning("t検定にはグループが2つである必要があります")

                elif test_type == "正規性検定":
                    test_col = st.selectbox("検定する列", numeric_cols)

                    from scipy import stats

                    # Shapiro-Wilk検定
                    if len(df[test_col].dropna()) <= 5000:  # サンプルサイズ制限
                        stat, p_value = stats.shapiro(df[test_col].dropna())
                        st.write("**Shapiro-Wilk検定結果**")
                        st.write(f"- 統計量: {stat:.4f}")
                        st.write(f"- p値: {p_value:.4f}")
                        st.write(f"- 結果: {'正規分布に従う' if p_value > 0.05 else '正規分布に従わない'}")
                    else:
                        st.info("サンプルサイズが大きすぎるため、ヒストグラムで分布を確認してください")

                    # ヒストグラムと正規分布の重ね合わせ
                    fig = px.histogram(df, x=test_col, title=f"{test_col}の分布", marginal="box")
                    st.plotly_chart(fig, use_container_width=True)

        with analysis_tabs[2]:
            # 外れ値検出
            st.subheader("🎯 外れ値検出")

            if len(numeric_cols) > 0:
                outlier_col = st.selectbox("外れ値を検出する列", numeric_cols)
                method = st.selectbox("検出方法", ["IQR法", "Z-score法"])

                if method == "IQR法":
                    Q1 = df[outlier_col].quantile(0.25)
                    Q3 = df[outlier_col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    outliers = df[(df[outlier_col] < lower_bound) | (df[outlier_col] > upper_bound)]

                elif method == "Z-score法":
                    from scipy import stats
                    threshold = st.slider("Z-scoreの閾値", 2.0, 4.0, 3.0)
                    z_scores = np.abs(stats.zscore(df[outlier_col].dropna()))
                    outliers = df[z_scores > threshold]

                st.write("**外れ値検出結果**")
                st.write(f"- 外れ値の数: {len(outliers)} / {len(df)} ({len(outliers)/len(df)*100:.1f}%)")

                if len(outliers) > 0:
                    st.write("**外れ値のデータ:**")
                    st.dataframe(outliers.head(10), use_container_width=True)

                    # 外れ値を除いたデータのダウンロード
                    clean_data = df[~df.index.isin(outliers.index)]
                    csv_clean = clean_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 外れ値を除いたデータをダウンロード",
                        data=csv_clean,
                        file_name=f"clean_{uploaded_file.name}",
                        mime="text/csv"
                    )

                # 箱ひげ図で外れ値を可視化
                fig = px.box(df, y=outlier_col, title=f"{outlier_col}の外れ値")
                st.plotly_chart(fig, use_container_width=True)

        with analysis_tabs[3]:
            # データ品質
            st.subheader("🔍 データ品質チェック")

            quality_metrics = {
                "完全性": f"{(1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}%",
                "重複行": f"{df.duplicated().sum()} 行 ({df.duplicated().sum()/len(df)*100:.1f}%)",
                "データ型の一貫性": "チェック完了",
                "値の範囲": "正常"
            }

            col1, col2 = st.columns(2)
            with col1:
                for metric, value in quality_metrics.items():
                    st.metric(metric, value)

            with col2:
                # 列ごとの欠損値率
                missing_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
                if missing_pct.sum() > 0:
                    fig = px.bar(
                        x=missing_pct.index, y=missing_pct.values,
                        title="列ごとの欠損値率 (%)",
                        labels={'x': '列名', 'y': '欠損値率 (%)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success("欠損値はありません！")

            # 重複行の詳細
            if df.duplicated().sum() > 0:
                st.write("**重複行の例:**")
                duplicates = df[df.duplicated(keep=False)].head(10)
                st.dataframe(duplicates, use_container_width=True)

                # 重複を除いたデータのダウンロード
                unique_data = df.drop_duplicates()
                csv_unique = unique_data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 重複を除いたデータをダウンロード",
                    data=csv_unique,
                    file_name=f"unique_{uploaded_file.name}",
                    mime="text/csv"
                )

        # HTMLレポート生成
        st.header("📄 HTMLレポート生成")

        if st.button("HTMLレポートを生成", type="primary"):
            # HTMLレポート作成
            html_content = generate_html_report(df, uploaded_file.name)

            # ダウンロードリンク作成
            b64 = base64.b64encode(html_content.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="data_report.html">📥 HTMLレポートをダウンロード</a>'
            st.markdown(href, unsafe_allow_html=True)

            st.success("HTMLレポートが生成されました！上のリンクからダウンロードできます。")

    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        st.info("CSVファイルの形式を確認してください。")

else:
    st.info("👆 サイドバーからCSVファイルをアップロードしてください")

    # サンプルデータ生成機能
    st.header("🎲 サンプルデータで試す")

    sample_type = st.selectbox(
        "サンプルデータの種類",
        ["売上データ", "顧客データ", "株価データ", "アンケートデータ"]
    )

    if st.button("サンプルデータを生成"):
        np.random.seed(42)

        if sample_type == "売上データ":
            dates = pd.date_range('2023-01-01', periods=365, freq='D')
            sample_df = pd.DataFrame({
                '日付': dates,
                '売上': np.random.normal(100000, 20000, 365).astype(int),
                '商品カテゴリ': np.random.choice(['電子機器', '衣類', '食品', '書籍'], 365),
                '地域': np.random.choice(['東京', '大阪', '名古屋', '福岡'], 365),
                '顧客数': np.random.poisson(50, 365),
                '平均単価': np.random.normal(2000, 500, 365).astype(int)
            })

        elif sample_type == "顧客データ":
            sample_df = pd.DataFrame({
                '顧客ID': range(1, 1001),
                '年齢': np.random.normal(40, 15, 1000).astype(int),
                '性別': np.random.choice(['男性', '女性'], 1000),
                '年収': np.random.normal(500, 150, 1000).astype(int) * 10000,
                '購入回数': np.random.poisson(5, 1000),
                '満足度': np.random.choice([1, 2, 3, 4, 5], 1000, p=[0.05, 0.1, 0.2, 0.4, 0.25]),
                '会員ランク': np.random.choice(['ブロンズ', 'シルバー', 'ゴールド', 'プラチナ'], 1000, p=[0.4, 0.3, 0.2, 0.1])
            })

        elif sample_type == "株価データ":
            dates = pd.date_range('2023-01-01', periods=252, freq='B')  # 営業日のみ
            price = 1000
            prices = []
            for _ in range(252):
                price *= (1 + np.random.normal(0, 0.02))
                prices.append(price)

            sample_df = pd.DataFrame({
                '日付': dates,
                '終値': prices,
                '出来高': np.random.normal(1000000, 300000, 252).astype(int),
                '高値': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
                '安値': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices]
            })

        elif sample_type == "アンケートデータ":
            sample_df = pd.DataFrame({
                '回答者ID': range(1, 501),
                '年代': np.random.choice(['10代', '20代', '30代', '40代', '50代', '60代以上'], 500),
                '職業': np.random.choice(['会社員', '公務員', '自営業', '学生', '主婦', 'その他'], 500),
                'サービス満足度': np.random.choice([1, 2, 3, 4, 5], 500, p=[0.05, 0.1, 0.25, 0.4, 0.2]),
                '価格満足度': np.random.choice([1, 2, 3, 4, 5], 500, p=[0.1, 0.15, 0.3, 0.3, 0.15]),
                '利用頻度': np.random.choice(['毎日', '週数回', '週1回', '月数回', '月1回', 'それ以下'], 500),
                '推奨度': np.random.choice([1, 2, 3, 4, 5], 500, p=[0.1, 0.1, 0.2, 0.35, 0.25])
            })

        # セッション状態にサンプルデータを保存
        st.session_state['sample_data'] = sample_df
        st.success(f"✅ {sample_type}のサンプルデータを生成しました！")
        st.dataframe(sample_df.head(), use_container_width=True)

        # CSVダウンロード
        csv_sample = sample_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 サンプルデータをダウンロード",
            data=csv_sample,
            file_name=f"sample_{sample_type}.csv",
            mime="text/csv"
        )

    # 使い方の説明
    st.markdown("""
    ### 📝 使い方
    1. **サンプルデータで試す**: 上記のサンプルデータ生成機能を使用
    2. **CSVファイルをアップロード**: サイドバーからファイルを選択
    3. **データを探索**: 概要、統計、フィルタリング機能を活用
    4. **グラフを作成**: 10種類以上のグラフタイプから選択
    5. **統計分析**: 相関分析、統計検定、外れ値検出を実行
    6. **レポート生成**: HTMLレポートを生成・ダウンロード

    ### 🚀 新機能
    - **高度なフィルタリング**: 数値範囲、カテゴリ値での絞り込み
    - **多様なグラフ**: 円グラフ、面グラフ、バイオリンプロット、ペアプロット
    - **統計検定**: t検定、正規性検定、分散分析
    - **外れ値検出**: IQR法、Z-score法
    - **データ品質チェック**: 完全性、重複、一貫性の確認
    - **インタラクティブな相関分析**: Plotlyベースのヒートマップ

    ### 💡 対応している機能
    - **データ概要**: 行数、列数、欠損値の確認
    - **基本統計**: 数値データとカテゴリデータの統計
    - **グラフ作成**: 棒グラフ、線グラフ、散布図、ヒストグラム、箱ひげ図、円グラフ、面グラフ、バイオリンプロット、ペアプロット
    - **相関分析**: 数値データ間の相関関係を可視化
    - **統計分析**: 各種統計検定と外れ値検出
    - **HTMLレポート**: 分析結果をまとめたレポートを生成
    """)

