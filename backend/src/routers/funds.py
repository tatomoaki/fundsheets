import hashlib
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.dependencies import db, get_db_session
from src.ingestion.persist import persist_fund_data
from src.ingestion.pipeline import DisclosurePipeline
from src.models.funds import Fund
from src.services.fund_service import FundService
from src.storage.repositories import FundRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/funds", tags=["funds"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@router.get("/", response_model=list[Fund])
def list_funds(session: Session = Depends(get_db_session)):
    fund_repo = FundRepository(session=session)
    service = FundService(fund_repo)
    return service.list_funds()


def _ingest_and_persist(pdf_path: Path) -> None:
    try:
        fund_data = DisclosurePipeline().run(str(pdf_path))
        with db.session() as session:
            persist_fund_data(session, fund_data)
    except Exception:
        logger.exception("Ingestion failed for %s", pdf_path)


@router.post("/upload", status_code=202)
async def upload_fund(file: UploadFile, background_tasks: BackgroundTasks):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    contents = await file.read()
    file_hash = hashlib.sha256(contents).hexdigest()
    pdf_path = UPLOAD_DIR / f"{file_hash}.pdf"
    if not pdf_path.exists():
        pdf_path.write_bytes(contents)

    background_tasks.add_task(_ingest_and_persist, pdf_path)
    return {"fund_hash": file_hash, "status": "processing"}
