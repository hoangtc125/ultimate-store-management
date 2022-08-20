import io
from typing import TypeVar
import pandas as pd
from fastapi.responses import StreamingResponse
from app.utils.time_utils import *
from fastapi import UploadFile

T = TypeVar("T")

def uploadfile_to_df(upload_file: UploadFile, skiprows: int):
    read_file = upload_file.file.read()
    xls_file_byteio = io.BytesIO(read_file)
    df = pd.read_excel(xls_file_byteio, engine='openpyxl', skiprows=skiprows)
    df.dropna(how='all', inplace=True)
    return df

def to_xls_streaming_response(
        dataframe: pd.DataFrame,
        filename: str,
        sheet_name: Optional[str] = "Sheet",
        title: Optional[str] = None,
        title_format: Optional[dict] = None,
        column_format: Optional[dict] = None,
        hidden_column: Optional[list] = None
        ):
    file_byteio = io.BytesIO()
    writer = pd.ExcelWriter(file_byteio, engine="xlsxwriter")
    dataframe.to_excel(
        writer,
        index=False,
        encoding="utf-8",
        engine="xlsxwriter",
        startrow=1 if title else 0,
        header=True,
        sheet_name=sheet_name,
    )
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    if title:
        title_format = workbook.add_format(title_format)
        worksheet.merge_range(0, 0, 0, len(dataframe.columns)-1, title, title_format)
        worksheet.set_row(0, 50)
    workbook.close()

    response = StreamingResponse(
        iter([file_byteio.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response.headers[
        "Content-Disposition"
    ] = "attachment; filename=" + filename + ".xlsx"
    return response

def dataframe_to_objs(dataframe: pd.DataFrame, access_column: dict, target : T):
    lst_objs = []
    obj_value = {}
    for index, row in dataframe.iterrows():
        for key, val in access_column.items():
            obj_value[key] = row[val] if not pd.isna(row[val]) else None
        if all(not value for value in obj_value.values()):
            obj = None
        else:
            obj = target(**obj_value)
        lst_objs.append(obj)
    return lst_objs