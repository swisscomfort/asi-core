#!/usr/bin/env python3
"""
ASI-Core Logo Generator
Erstellt ein professionelles Logo für das ASI-Core Projekt
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np

def create_asi_logo():
    # Erstelle Figure mit GitHub Social Media Größe (1280x640)
    fig, ax = plt.subplots(figsize=(12.8, 6.4), dpi=100)
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 6.4)
    ax.set_aspect('equal')
    
    # Hintergrund: Gradient von dunkelblau zu schwarz
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    ax.imshow(gradient, extent=[0, 12.8, 0, 6.4], aspect='auto', cmap='Blues_r', alpha=0.8)
    
    # Hauptkreis (Gehirn/Core Symbol)
    brain_center = Circle((4.5, 3.2), 1.5, color='#00D4AA', alpha=0.8, linewidth=3, fill=False)
    ax.add_patch(brain_center)
    
    # Innere Verbindungen (Neuronales Netzwerk)
    for i in range(8):
        angle = i * np.pi / 4
        x1 = 4.5 + 0.7 * np.cos(angle)
        y1 = 3.2 + 0.7 * np.sin(angle)
        x2 = 4.5 + 1.3 * np.cos(angle)
        y2 = 3.2 + 1.3 * np.sin(angle)
        ax.plot([x1, x2], [y1, y2], color='#00D4AA', linewidth=2, alpha=0.6)
        
        # Kleine Punkte an den Enden
        ax.plot(x2, y2, 'o', color='#00D4AA', markersize=4)
    
    # Blockchain-Blöcke (rechts)
    block_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    for i, color in enumerate(block_colors):
        x = 7.5 + i * 0.8
        y = 3.2
        block = FancyBboxPatch((x-0.3, y-0.3), 0.6, 0.6, 
                              boxstyle="round,pad=0.05", 
                              facecolor=color, alpha=0.7,
                              edgecolor='white', linewidth=2)
        ax.add_patch(block)
        
        # Verbindungslinien zwischen Blöcken
        if i < len(block_colors) - 1:
            ax.plot([x+0.3, x+0.5], [y, y], color='white', linewidth=2, alpha=0.8)
    
    # Dezentrale Speicher-Knoten (links oben)
    storage_positions = [(2, 5), (3, 5.5), (1.5, 4.5)]
    for x, y in storage_positions:
        storage = Circle((x, y), 0.15, color='#FFD93D', alpha=0.8)
        ax.add_patch(storage)
        # Verbindung zum Hauptcore
        ax.plot([x, 4.5], [y, 3.2], color='#FFD93D', linewidth=1, alpha=0.4, linestyle='--')
    
    # Haupttitel: ASI-CORE
    ax.text(6.4, 4.5, 'ASI-CORE', fontsize=48, fontweight='bold', 
            color='white', ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
    
    # Untertitel
    ax.text(6.4, 3.8, 'Hybrid AI Reflection System', fontsize=16, 
            color='#00D4AA', ha='center', va='center', style='italic')
    
    # Technologie-Tags
    technologies = ['Python', 'Blockchain', 'IPFS', 'React', 'PWA']
    for i, tech in enumerate(technologies):
        x = 6.4 + (i-2) * 1.2
        y = 2.8
        tech_box = FancyBboxPatch((x-0.4, y-0.15), 0.8, 0.3,
                                 boxstyle="round,pad=0.05",
                                 facecolor='#2C3E50', alpha=0.8,
                                 edgecolor='#00D4AA', linewidth=1)
        ax.add_patch(tech_box)
        ax.text(x, y, tech, fontsize=9, color='white', ha='center', va='center')
    
    # GitHub URL
    ax.text(6.4, 1.8, 'github.com/swisscomfort/asi-core', fontsize=12, 
            color='#7F8C8D', ha='center', va='center')
    
    # Zusätzliche Design-Elemente: Partikel-Effekt
    np.random.seed(42)  # Für konsistente Ergebnisse
    for _ in range(50):
        x = np.random.uniform(0, 12.8)
        y = np.random.uniform(0, 6.4)
        size = np.random.uniform(1, 3)
        alpha = np.random.uniform(0.1, 0.3)
        ax.plot(x, y, 'o', color='white', markersize=size, alpha=alpha)
    
    # Entferne Achsen
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Speichern
    plt.tight_layout()
    plt.savefig('/workspaces/asi-core/ASI-Core-Logo.png', 
                dpi=100, bbox_inches='tight', pad_inches=0.1,
                facecolor='black', edgecolor='none')
    plt.savefig('/workspaces/asi-core/ASI-Core-Logo-HiRes.png', 
                dpi=200, bbox_inches='tight', pad_inches=0.1,
                facecolor='black', edgecolor='none')
    
    print("✅ Logo erstellt:")
    print("   - ASI-Core-Logo.png (1280x640px für GitHub)")
    print("   - ASI-Core-Logo-HiRes.png (2560x1280px High-Res)")
    
    plt.show()

if __name__ == "__main__":
    create_asi_logo()