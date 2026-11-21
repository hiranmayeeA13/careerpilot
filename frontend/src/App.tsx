import { HashRouter, Routes, Route } from 'react-router-dom';
import { CandidateProvider } from './state/CandidateContext';
import { ThemeProvider } from './state/ThemeContext';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Simulator } from './pages/Simulator';
import { CareerTwin } from './pages/CareerTwin';
import { RealityCheck } from './pages/RealityCheck';
import { Portfolio } from './pages/Portfolio';
import { Compare } from './pages/Compare';
import { Intake } from './pages/Intake';
import { JobMarket } from './pages/JobMarket';
import { LearningPlan } from './pages/LearningPlan';
import { MockInterview } from './pages/MockInterview';
import { Applications } from './pages/Applications';
import { AboutMe } from './pages/AboutMe';

export default function App() {
  return (
    <ThemeProvider>
      <CandidateProvider>
        <HashRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/about-me" element={<AboutMe />} />
              <Route path="/intake" element={<Intake />} />
              <Route path="/simulator" element={<Simulator />} />
              <Route path="/twin" element={<CareerTwin />} />
              <Route path="/job-market" element={<JobMarket />} />
              <Route path="/plan" element={<LearningPlan />} />
              <Route path="/reality-check" element={<RealityCheck />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/mock-interview" element={<MockInterview />} />
              <Route path="/applications" element={<Applications />} />
              <Route path="/compare" element={<Compare />} />
            </Route>
          </Routes>
        </HashRouter>
      </CandidateProvider>
    </ThemeProvider>
  );
}
