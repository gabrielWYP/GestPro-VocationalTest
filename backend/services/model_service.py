import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def recomendar_carreras(respuestas_intereses, respuestas_habilidades, df_base, 
                        peso_intereses=0.6, peso_habilidades=0.4):
    """
    Recomienda carreras basado en Intereses + Habilidades ponderadas.
    
    Args:
        respuestas_intereses: dict con R1-4, I1-4, A1-4, S1-4, E1-4, C1-4
        respuestas_habilidades: dict con R1-2, I1-2, A1-2, S1-2, E1-2, C1-2
        df_base: DataFrame con ocupaciones y puntajes O*NET
        peso_intereses: peso del vector de intereses (0-1)
        peso_habilidades: peso del vector de habilidades (0-1)
    """
    
    # --- MAPEO DE COLUMNAS ---
    col_map = {
        'R': 'Realistic',
        'I': 'Investigative',
        'A': 'Artistic',
        'S': 'Social',
        'E': 'Enterprising',
        'C': 'Conventional'
    }
    ordered_cols = [col_map[k] for k in ['R', 'I', 'A', 'S', 'E', 'C']]

    # --- PROCESAR INTERESES ---
    scores_int = {
        'R': np.mean([respuestas_intereses['R1'], respuestas_intereses['R2'], 
                      respuestas_intereses['R3'], respuestas_intereses['R4']]),
        'I': np.mean([respuestas_intereses['I1'], respuestas_intereses['I2'], 
                      respuestas_intereses['I3'], respuestas_intereses['I4']]),
        'A': np.mean([respuestas_intereses['A1'], respuestas_intereses['A2'], 
                      respuestas_intereses['A3'], respuestas_intereses['A4']]),
        'S': np.mean([respuestas_intereses['S1'], respuestas_intereses['S2'], 
                      respuestas_intereses['S3'], respuestas_intereses['S4']]),
        'E': np.mean([respuestas_intereses['E1'], respuestas_intereses['E2'], 
                      respuestas_intereses['E3'], respuestas_intereses['E4']]),
        'C': np.mean([respuestas_intereses['C1'], respuestas_intereses['C2'], 
                      respuestas_intereses['C3'], respuestas_intereses['C4']])
    }
    vector_int = np.array([scores_int[k] for k in ['R', 'I', 'A', 'S', 'E', 'C']])
    vector_int_norm = (vector_int - 3) / 2.0  # 1-5 -> -1 a 1

    # --- PROCESAR HABILIDADES ---
    scores_hab = {
        'R': np.mean([respuestas_habilidades['R1'], respuestas_habilidades['R2']]),
        'I': np.mean([respuestas_habilidades['I1'], respuestas_habilidades['I2']]),
        'A': np.mean([respuestas_habilidades['A1'], respuestas_habilidades['A2']]),
        'S': np.mean([respuestas_habilidades['S1'], respuestas_habilidades['S2']]),
        'E': np.mean([respuestas_habilidades['E1'], respuestas_habilidades['E2']]),
        'C': np.mean([respuestas_habilidades['C1'], respuestas_habilidades['C2']])
    }
    vector_hab = np.array([scores_hab[k] for k in ['R', 'I', 'A', 'S', 'E', 'C']])
    vector_hab_norm = (vector_hab - 3) / 2.0  # 1-5 -> -1 a 1

    # --- VECTOR COMBINADO (PONDERADO) ---
    vector_combinado = (vector_int_norm * peso_intereses + 
                        vector_hab_norm * peso_habilidades)

    # --- IMPRIMIR PERFIL RIASEC DEL ESTUDIANTE ---
    print("\n" + "=" * 70)
    print("📊 PERFIL RIASEC DEL ESTUDIANTE (Escala 1-5)")
    print("=" * 70)
    
    riasec_labels = ['R (Realistic)', 'I (Investigative)', 'A (Artistic)', 
                     'S (Social)', 'E (Enterprising)', 'C (Conventional)']
    
    print("\n▶ INTERESES (40%):")
    for i, label in enumerate(riasec_labels):
        val_int = vector_int[i]
        print(f"   {label:20} | {val_int:5.2f} ", end="")
        print("█" * int(val_int * 2) + "░" * (10 - int(val_int * 2)))
    
    print("\n▶ HABILIDADES (30%):")
    for i, label in enumerate(riasec_labels):
        val_hab = vector_hab[i]
        print(f"   {label:20} | {val_hab:5.2f} ", end="")
        print("█" * int(val_hab * 2) + "░" * (10 - int(val_hab * 2)))
    
    print("\n▶ VECTOR COMBINADO (PONDERADO):")
    for i, label in enumerate(riasec_labels):
        val_comb = vector_combinado[i]
        print(f"   {label:20} | {val_comb:6.3f}")
    
    print("=" * 70)

    # --- PROCESAR BASE DE DATOS ---
    df_calc = df_base.copy()
    df_calc[ordered_cols] = (df_calc[ordered_cols] - 1) / 6.0

    # --- CALCULAR SIMILITUD ---
    similarities = cosine_similarity(
        vector_combinado.reshape(1, -1),
        df_calc[ordered_cols]
    )
    df_calc['Match_Score'] = similarities[0]

    # --- RETORNAR RESULTADOS ---
    resultado = df_calc.sort_values(by='Match_Score', ascending=False)
    return resultado[['Ocupacion', 'Match_Score', 'Posibles carreras']]