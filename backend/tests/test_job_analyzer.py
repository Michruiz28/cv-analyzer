"""
Script de prueba para Job Analyzer Agent
"""
from agents.job_analyzer import JobAnalyzerAgent

def test_job_analyzer():
    """Prueba el Job Analyzer con un ejemplo"""
    
    sample_job = """
    Senior Full-Stack Developer
    TechCorp Inc. - Remote
    
    We are seeking an experienced Senior Full-Stack Developer.
    
    Responsibilities:
    - Design and develop web applications using React and Node.js
    - Lead technical discussions and code reviews
    - Mentor junior developers
    - Optimize performance and scalability
    
    Requirements:
    - 5+ years of full-stack development experience
    - Strong proficiency in JavaScript, React, Node.js, TypeScript
    - Experience with AWS or Azure
    - Knowledge of Docker and Kubernetes
    - Bachelor's degree in Computer Science
    
    Nice to Have:
    - Experience with microservices
    - Knowledge of Python or Go
    - AWS certifications
    
    Benefits:
    - Salary: $140k - $180k
    - Full remote work
    - Health insurance
    - Professional development budget
    """
    
    print(" INICIANDO TEST DEL JOB ANALYZER AGENT")
    print("="*70 + "\n")
    
    try:
        # Crear agente
        agent = JobAnalyzerAgent()
        
        # Procesar trabajo
        job = agent.process_job_from_text(sample_job, generate_summary=True)
        
        # Mostrar resultados
        agent.print_analysis_summary(job)
        
        # Guardar
        agent.save_analysis(job, "test_job_analysis.json")
        
        print(" TEST COMPLETADO EXITOSAMENTE")
        print(" Revisa 'test_job_analysis.json' para ver el resultado\n")
        
    except Exception as e:
        print(f"❌ TEST FALLÓ: {str(e)}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_job_analyzer()
