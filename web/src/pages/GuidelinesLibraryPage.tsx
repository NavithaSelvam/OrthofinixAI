import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Book, ChevronRight, Search } from 'lucide-react';

export interface GuidelineInfo {
  id: string;
  name: string;
  category: string;
  description: string;
  keyPoints: string[];
  clinicalSignificance: string;
}

export const guidelinesData: GuidelineInfo[] = [
  {
    id: 'abo-ogs',
    name: 'ABO Objective Grading System (OGS)',
    category: 'Finishing Index',
    description: 'The global gold standard for board-level orthodontic finishing assessment and case examination.',
    keyPoints: [
      'Alignment and Leveling (anterior incisal & posterior marginal ridges)',
      'Marginal Ridge Heights (adjacent premolars and molars within 0.5mm)',
      'Buccolingual Inclination (avoiding excessive lingual cusp hanging)',
      'Occlusal Contacts (functional contact across all premolar/molar cusps)',
      'Occlusal Relationships (Class I canine and molar intercuspation)',
      'Overjet & Anterior Crossbite (proper 1-3mm contact with guidance)',
      'Interproximal Contacts (tight, closed contacts without food traps)',
      'Root Angulation (parallel roots on panoramic radiograph)'
    ],
    clinicalSignificance: 'ABO OGS scoring ensures board-certified finishing quality, post-treatment stability, and balanced periodontal health.'
  },
  {
    id: 'andrews-keys',
    name: "Andrews' Six Keys to Normal Occlusion",
    category: 'Occlusal Fundamentals',
    description: 'The six fundamental morphological characteristics observed in naturally optimal non-orthodontic occlusions.',
    keyPoints: [
      'Key 1: Molar Relationship (mesiobuccal cusp into mesiobuccal groove & distal cusp contacts)',
      'Key 2: Crown Angulation / Tip (gingival portion located distal to incisal portion)',
      'Key 3: Crown Inclination / Torque (anterior labial/lingual torque & posterior lingual crown inclination)',
      'Key 4: Absence of Rotations (teeth free of undesirable rotations)',
      'Key 5: Tight Contacts (no interdental spaces present)',
      'Key 6: Flat Curve of Spee (depth ≤ 1.5mm for optimal mandibular excursion)'
    ],
    clinicalSignificance: 'Forms the foundational biomechanical blueprint for straight-wire bracket prescriptions and functional occlusion.'
  },
  {
    id: 'roling-concepts',
    name: "Dr. Rebecca Roling's Finishing Concepts",
    category: 'Functional Stability',
    description: 'Practical clinical guidelines focusing on arch form symmetry, canine seating, and long-term functional stability.',
    keyPoints: [
      'Maxillary Intercanine Width Stability',
      'Solid Canine Guidance without Balance Interferences',
      'Torque Expression in Maxillary Lateral Incisors',
      'Marginal Ridge Alignment between Upper 4s and 5s',
      'Second Molar Control and Alignment'
    ],
    clinicalSignificance: 'Prevents relapse and ensures aesthetic smile arc curvature consonant with the lower lip.'
  },
  {
    id: 'raleigh-williams',
    name: 'Raleigh-Williams Keys to Excellence',
    category: 'Clinical Finishing',
    description: 'Detailed criteria for finishing orthodontic cases with aesthetic and gnathological precision.',
    keyPoints: [
      'Parallel roots verified on panoramic radiograph',
      'Flat or gentle curve of Spee (< 1.0mm)',
      'Correct anterior torque for solid incisal stops',
      'Centric relation coinciding with centric occlusion',
      'Smooth canine protected excursion'
    ],
    clinicalSignificance: 'Ensures functional masticatory comfort and protects against temporomandibular joint dysfunction.'
  },
  {
    id: 'ricketts-analysis',
    name: 'Ricketts / Merrifield Analysis',
    category: 'Cephalometric & Skeletal',
    description: 'Cephalometric, profile, and skeletal finishing criteria for facial balance and profile harmony.',
    keyPoints: [
      'Esthetic Plane (E-line) lip positions',
      'Lower Incisor to A-Pog line (1-3mm ideal)',
      'Facial Axis & Mandibular Plane stability',
      'Total Space Analysis for arch length discrepancy'
    ],
    clinicalSignificance: 'Maintains soft tissue profile harmony and avoids excessive lip protrusion or retrusion.'
  },
  {
    id: 'roth-williams',
    name: 'Roth / Williams Philosophy',
    category: 'Gnathological Philosophy',
    description: 'Functional occlusion, seated condylar position (CR-CO harmony), and mutually protected occlusion.',
    keyPoints: [
      'Condyles seated in anterior-superior position (Centric Relation)',
      'Mutually protected occlusion with anterior guidance',
      'No balancing / non-working side interferences',
      'Optimized posterior disclusion during lateral & protrusive excursions'
    ],
    clinicalSignificance: 'Eliminates occlusal trauma and protects restorative dentistry longevity.'
  }
];

export default function GuidelinesLibraryPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredGuidelines = guidelinesData.filter((g) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      g.name.toLowerCase().includes(q) ||
      g.description.toLowerCase().includes(q) ||
      g.category.toLowerCase().includes(q)
    );
  });

  return (
    <div className="flex-1 flex flex-col bg-[#F8FAFC] dark:bg-[#0F172A] pb-24 font-sans">
      
      {/* TopAppBar matching Android Scaffold */}
      <header className="bg-white dark:bg-[#1E293B] border-b border-[#E2E8F0] dark:border-slate-800 h-14 flex items-center px-4 sticky top-0 z-30 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#1A5296] text-white font-black text-sm">
            O
          </div>
          <span className="text-base font-bold text-slate-900 dark:text-white">
            Guidelines Library
          </span>
        </div>
      </header>

      {/* Main Column */}
      <div className="p-4 space-y-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            Clinical References
          </h2>
          <p className="text-sm text-[#808080] dark:text-slate-400 mt-0.5">
            Access standard orthodontic indices and principles
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#64748B]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search guidelines or rules..."
            className="w-full pl-10 pr-4 py-3 text-xs font-medium rounded-xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 focus:border-[#76B82A] outline-none transition text-slate-900 dark:text-white shadow-2xs"
          />
        </div>

        {/* Guidelines List matching Android GuidelineCard */}
        <div className="space-y-3">
          {filteredGuidelines.map((guideline) => (
            <div
              key={guideline.id}
              onClick={() => navigate(`/guidelines/${guideline.id}`)}
              className="cursor-pointer p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-[#E2E8F0] dark:border-slate-800 hover:shadow-md transition flex items-center gap-3.5 shadow-2xs"
            >
              <div className="w-12 h-12 rounded-xl bg-[#76B82A]/10 flex items-center justify-center text-[#76B82A] shrink-0">
                <Book size={24} />
              </div>

              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-bold text-slate-900 dark:text-white truncate">
                  {guideline.name}
                </h4>
                <p className="text-xs text-[#808080] dark:text-slate-400 line-clamp-2 mt-0.5">
                  {guideline.description}
                </p>
              </div>

              <ChevronRight size={18} className="text-[#808080] shrink-0" />
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
