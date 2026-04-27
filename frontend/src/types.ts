/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface EntmanPillars {
  problemDefinition: string;
  causalInterpretation: string;
  moralEvaluation: string;
  treatmentRecommendation: string;
}

export interface ActorSentiment {
  name: string;
  relevance: number; // 0-100
  sentiment: 'positive' | 'negative' | 'neutral';
  role: string;
}

export interface NewsAnalysis {
  title: string;
  source: string;
  summary: string;
  framing: EntmanPillars;
  actors: ActorSentiment[];
  keywords: string[];
  overallSentiment: number; // -1 to 1
}

export interface ComparativeReport {
  summary: string;
  keyDifferences: string[];
  sharedNarratives: string[];
  biasIndicator: string;
}

export type AnalysisResult = {
  analyses: NewsAnalysis[];
  comparativeReport: ComparativeReport;
};
