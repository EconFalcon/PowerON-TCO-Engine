import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import CalculatorPage from './pages/CalculatorPage';
import ScenariosPage from './pages/ScenariosPage';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<CalculatorPage />} />
          <Route path="/scenarios" element={<ScenariosPage />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}

export default App;
