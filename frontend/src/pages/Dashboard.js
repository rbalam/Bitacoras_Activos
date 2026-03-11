import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { getDashboardStats, getAlerts } from '../utils/api';
import { 
  Package, 
  Wrench, 
  AlertTriangle, 
  CheckCircle, 
  Bell,
  TrendingUp,
  ArrowRight
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, alertsRes] = await Promise.all([
        getDashboardStats(),
        getAlerts({ leida: false })
      ]);
      setStats(statsRes.data);
      setAlerts(alertsRes.data.slice(0, 5));
    } catch (error) {
      toast.error('Error al cargar datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900"></div>
        </div>
      </Layout>
    );
  }

  const statCards = [
    {
      title: 'Total Activos',
      value: stats?.total_assets || 0,
      icon: Package,
      color: 'text-slate-700',
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200'
    },
    {
      title: 'Operativos',
      value: stats?.assets_operativos || 0,
      icon: CheckCircle,
      color: 'text-emerald-700',
      bgColor: 'bg-emerald-50',
      borderColor: 'border-emerald-200'
    },
    {
      title: 'En Mantenimiento',
      value: stats?.assets_mantenimiento || 0,
      icon: Wrench,
      color: 'text-blue-700',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200'
    },
    {
      title: 'Críticos',
      value: stats?.assets_criticos || 0,
      icon: AlertTriangle,
      color: 'text-red-700',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200'
    }
  ];

  return (
    <Layout>
      <div className="space-y-6" data-testid="dashboard-page">
        {/* Header */}
        <div>
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight" style={{ fontFamily: 'Chivo, sans-serif' }}>
            Dashboard
          </h1>
          <p className="mt-2 text-base text-slate-600 leading-relaxed">
            Visión general del estado de tus activos
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map((stat, index) => (
            <Card 
              key={index}
              className={`p-6 bg-white border shadow-sm rounded-sm hover:border-slate-300 transition-colors ${stat.borderColor}`}
              data-testid={`stat-card-${stat.title.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-600">
                    {stat.title}
                  </p>
                  <p className="mt-2 text-3xl font-bold text-slate-900">
                    {stat.value}
                  </p>
                </div>
                <div className={`p-3 rounded-sm ${stat.bgColor} ${stat.borderColor} border`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pending Items */}
          <Card className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Chivo, sans-serif' }}>
                Pendientes
              </h2>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-sm">
                <div className="flex items-center">
                  <Wrench className="h-5 w-5 text-blue-700 mr-3" />
                  <span className="text-sm font-medium text-blue-900">Mantenimientos Pendientes</span>
                </div>
                <Badge className="bg-blue-700 text-white" data-testid="pending-maintenances">
                  {stats?.mantenimientos_pendientes || 0}
                </Badge>
              </div>
              <div className="flex items-center justify-between p-4 bg-orange-50 border border-orange-200 rounded-sm">
                <div className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-orange-700 mr-3" />
                  <span className="text-sm font-medium text-orange-900">Autorizaciones Pendientes</span>
                </div>
                <Badge className="bg-orange-700 text-white" data-testid="pending-authorizations">
                  {stats?.autorizaciones_pendientes || 0}
                </Badge>
              </div>
              <Button 
                variant="ghost" 
                className="w-full justify-between hover:bg-slate-100"
                onClick={() => navigate('/maintenances')}
                data-testid="view-all-pending-button"
              >
                Ver todos
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </Card>

          {/* Recent Alerts */}
          <Card className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Chivo, sans-serif' }}>
                Alertas Recientes
              </h2>
              <Bell className="h-5 w-5 text-slate-400" />
            </div>
            {alerts.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-8">No hay alertas activas</p>
            ) : (
              <div className="space-y-3">
                {alerts.map((alert) => {
                  const priorityColors = {
                    baja: 'bg-slate-50 text-slate-700 border-slate-200',
                    media: 'bg-blue-50 text-blue-700 border-blue-200',
                    alta: 'bg-orange-50 text-orange-700 border-orange-200',
                    critica: 'bg-red-50 text-red-700 border-red-200'
                  };
                  return (
                    <div 
                      key={alert.id} 
                      className={`p-3 border rounded-sm ${priorityColors[alert.prioridad]}`}
                      data-testid={`alert-${alert.id}`}
                    >
                      <p className="text-sm font-semibold">{alert.titulo}</p>
                      <p className="text-xs mt-1 opacity-90">{alert.mensaje}</p>
                    </div>
                  );
                })}
                <Button 
                  variant="ghost" 
                  className="w-full justify-between hover:bg-slate-100"
                  onClick={() => navigate('/alerts')}
                  data-testid="view-all-alerts-button"
                >
                  Ver todas las alertas
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            )}
          </Card>
        </div>

        {/* Monthly Spending */}
        <Card className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Chivo, sans-serif' }}>
                Gasto del Mes Actual
              </h2>
              <p className="text-sm text-slate-600 mt-1">Total invertido en mantenimientos</p>
            </div>
            <div className="flex items-center">
              <TrendingUp className="h-6 w-6 text-emerald-600 mr-2" />
              <span className="text-3xl font-bold text-slate-900" data-testid="monthly-spending">
                ${(stats?.gasto_mes_actual || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default Dashboard;
