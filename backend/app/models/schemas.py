from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class FramingModel(BaseModel):
    """Skema untuk analisis framing Robert Entman (camelCase keys untuk React)."""
    problemDefinition: str = Field(description="Apa yang dianggap sebagai masalah utama dalam narasi?")
    causalInterpretation: str = Field(description="Siapa atau apa yang dianggap sebagai penyebab atau aktor di balik isu tersebut?")
    moralEvaluation: str = Field(description="Bagaimana penilaian etika atau 'pahlawan vs penjahat' diterapkan?")
    treatmentRecommendation: str = Field(description="Apa solusi yang ditawarkan atau diimplikasikan oleh media?")


class ActorModel(BaseModel):
    """Skema untuk aktor yang teridentifikasi dalam artikel."""
    name: str = Field(description="Nama aktor (tokoh, kelompok, atau lembaga).")
    relevance: int = Field(description="Tingkat relevansi aktor dalam artikel, skala 0-100.", ge=0, le=100)
    sentiment: Literal["positive", "negative", "neutral"] = Field(description="Sentimen terhadap aktor ini.")
    role: str = Field(description="Peran aktor dalam narasi, contoh: Decision Maker, Victim, Expert.")


class NewsAnalysisModel(BaseModel):
    """Skema lengkap hasil analisis satu artikel berita."""
    title: str = Field(description="Judul artikel.")
    source: str = Field(description="Nama sumber media/domain.")
    summary: str = Field(description="Ringkasan singkat framing artikel dalam 1-2 kalimat.")
    framing: FramingModel
    actors: List[ActorModel] = Field(description="Daftar 3-5 aktor utama.")
    keywords: List[str] = Field(description="Daftar 4-6 kata kunci paling penting dari artikel.")
    overallSentiment: float = Field(description="Skor sentimen keseluruhan dari -1.0 (sangat negatif) hingga 1.0 (sangat positif).", ge=-1.0, le=1.0)


class ComparativeReportModel(BaseModel):
    """Skema laporan komparatif antar beberapa artikel."""
    summary: str = Field(description="Ringkasan perbandingan framing antar media.")
    keyDifferences: List[str] = Field(description="Poin-poin perbedaan utama antar media.")
    sharedNarratives: List[str] = Field(description="Narasi atau sudut pandang yang sama antar media.")
    biasIndicator: str = Field(description="Indikasi bias yang terdeteksi dari perbandingan framing.")


class AnalysisResultModel(BaseModel):
    """Skema respons API final yang dikirimkan ke React frontend."""
    analyses: List[NewsAnalysisModel]
    comparativeReport: ComparativeReportModel


class ResearchRequest(BaseModel):
    """Request body untuk mencari berita berdasarkan topik."""
    topic: str = Field(description="Topik atau kata kunci berita yang dicari.")


class ResearchArticleSchema(BaseModel):
    """Skema artikel hasil temuan agent untuk dikirim ke frontend."""
    title: str
    source: str
    url: str
    snippet: str
    reason: str
    publishedDate: Optional[str] = None
    relevanceScore: int = 0


class ResearchResponse(BaseModel):
    """Respons API berisi list artikel hasil riset agent."""
    articles: List[ResearchArticleSchema]
    isFallback: bool = False
