/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from "react";
import { DataProvider, useData } from "./context/DataContext";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { HomePage } from "./components/pages/HomePage";
import { DataExplorerPage } from "./components/pages/DataExplorerPage";
import { EdaDashboardPage } from "./components/pages/EdaDashboardPage";
import { FeatureEngineeringPage } from "./components/pages/FeatureEngineeringPage";
import { ModelEvaluationPage } from "./components/pages/ModelEvaluationPage";
import { PredictiveInferencePage } from "./components/pages/PredictiveInferencePage";
import { RetentionDashboardPage } from "./components/pages/RetentionDashboardPage";
import { BusinessRecommendationsPage } from "./components/pages/BusinessRecommendationsPage";
import { ResponsibleMlPage } from "./components/pages/ResponsibleMlPage";
import { CodeExplorerPage } from "./components/pages/CodeExplorerPage";
import { VivaMentorPage } from "./components/pages/VivaMentorPage";
import { GlobalDataOverview } from "./components/GlobalDataOverview";
import { UploadModal } from "./components/UploadModal";

const MainContent: React.FC = () => {
  const { activePage } = useData();

  const renderActivePage = () => {
    switch (activePage) {
      case "home":
        return <HomePage />;
      case "global_overview":
        return <GlobalDataOverview />;
      case "explorer":
        return <DataExplorerPage />;
      case "eda":
        return <EdaDashboardPage />;
      case "features":
        return <FeatureEngineeringPage />;
      case "models":
        return <ModelEvaluationPage />;
      case "inference":
        return <PredictiveInferencePage />;
      case "retention":
        return <RetentionDashboardPage />;
      case "recommendations":
        return <BusinessRecommendationsPage />;
      case "responsible_ml":
        return <ResponsibleMlPage />;
      case "code":
        return <CodeExplorerPage />;
      case "viva":
        return <VivaMentorPage />;
      default:
        return <HomePage />;
    }
  };

  return (
    <main className="flex-1 overflow-y-auto p-4 lg:p-6 custom-scrollbar bg-slate-950 text-slate-100">
      <div className="max-w-7xl mx-auto pb-12">
        {renderActivePage()}
      </div>
    </main>
  );
};

const AppShell: React.FC = () => {
  const { isUploadModalOpen, setIsUploadModalOpen } = useData();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      <Header />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <MainContent />
      </div>
      <UploadModal isOpen={isUploadModalOpen} onClose={() => setIsUploadModalOpen(false)} />
    </div>
  );
};

export default function App() {
  return (
    <DataProvider>
      <AppShell />
    </DataProvider>
  );
}
