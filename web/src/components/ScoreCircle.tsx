import { motion } from 'framer-motion';

export function ScoreCircle({ score, label }: { score: number; label: string }) {
  const color = score >= 85 ? '#2BB673' : score >= 70 ? '#2563EB' : '#F59E0B';
  return (
    <div className="flex flex-col items-center">
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        className="relative flex h-36 w-36 items-center justify-center rounded-full"
        style={{
          background: `conic-gradient(${color} ${score * 3.6}deg, #e2e8f0 0deg)`,
        }}
      >
        <div className="flex h-28 w-28 flex-col items-center justify-center rounded-full bg-white dark:bg-slate-900">
          <span className="text-3xl font-black" style={{ color }}>
            {score.toFixed(0)}
          </span>
          <span className="text-xs text-slate-500">/ 100</span>
        </div>
      </motion.div>
      <p className="mt-3 font-semibold text-slate-700 dark:text-slate-200">{label}</p>
    </div>
  );
}
