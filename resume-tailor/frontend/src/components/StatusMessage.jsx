import { useEffect, useState } from 'react'

const STEPS = [
  { label: 'Parsing your resume…', threshold: 0 },
  { label: 'Analyzing job requirements with Claude AI…', threshold: 25 },
  { label: 'Generating tailored content…', threshold: 55 },
  { label: 'Creating your PDF…', threshold: 85 },
]

export default function StatusMessage({ progress }) {
  const step = [...STEPS].reverse().find((s) => progress >= s.threshold) || STEPS[0]

  return (
    <div className="bg-brand-pale border border-brand/20 rounded-xl p-6 text-center">
      <div className="flex justify-center mb-3">
        <svg className="animate-spin h-8 w-8 text-brand" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
      </div>
      <p className="text-brand font-semibold mb-4">{step.label}</p>
      <div className="w-full bg-white rounded-full h-2.5 overflow-hidden border border-brand/10">
        <div
          className="h-2.5 rounded-full bg-brand transition-all duration-700"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-xs text-gray-400 mt-2">{progress}%</p>
    </div>
  )
}
