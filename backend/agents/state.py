from typing import TypedDict, Optional

class AgentState(TypedDict):
    # Input dari user
    cv: str
    job_description: str
    
    # Output analisis kecocokan CV
    analysis: Optional[str]
    
    # Output cover letter yang dihasilkan
    cover_letter: Optional[str]
    
    # Masukan/Feedback dari user untuk revisi
    feedback: Optional[str]
    
    # Status alur kerja untuk UI visualizer
    status: str
    
    # Jumlah iterasi revisi yang sudah dilakukan
    revision_count: int
