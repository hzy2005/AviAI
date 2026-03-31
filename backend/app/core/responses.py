from fastapi.responses import JSONResponse


def success(data, message: str = "ok", status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content={
            "code": 0,
            "message": message,
            "data": data,
        },
    )


def error(code: int, message: str, status_code: int, data=None):
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "data": data,
        },
    )
