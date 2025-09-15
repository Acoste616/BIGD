/**
 * Główna strona Dashboard
 * Wyświetla listę sesji w głównym layoutcie
 */
import React from 'react';
import MainLayout from '../components/MainLayout';
import SessionList from '../components/SessionList';

const Dashboard = () => {
  return (
    <MainLayout title="Dashboard - Lista Sesji">
      <SessionList />
    </MainLayout>
  );
};

export default Dashboard;