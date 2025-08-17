/**
 * Główna strona Dashboard
 * Wyświetla listę klientów w głównym layoutcie
 */
import React from 'react';
import MainLayout from '../components/MainLayout';
import ClientList from '../components/ClientList';

const Dashboard = () => {
  return (
    <MainLayout title="Dashboard - Lista Klientów">
      <ClientList />
    </MainLayout>
  );
};

export default Dashboard;
