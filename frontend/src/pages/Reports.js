import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { getMaintenanceHistory, getAssets } from '../utils/api';
import { FileText, Download, Filter, Calendar } from 'lucide-react';
import { toast } from 'sonner';

const Reports = () => {
  const [maintenances, setMaintenances] = useState([]);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    asset_id: 'all',
    start_date: '',
    end_date: '',
    tipo: 'all'
  });

  useEffect(() => {
    fetchAssets();
  }, []);

  useEffect(() => {
    fetchMaintenances();
  }, [filters]);

  const fetchAssets = async () => {
    try {
      const response = await getAssets();
      setAssets(response.data);
    } catch (error) {
      toast.error('Error al cargar activos');
    }
  };

  const fetchMaintenances = async () => {
    try {
      setLoading(true);
      const response = await getMaintenanceHistory(filters);
      setMaintenances(response.data.maintenances || []);
    } catch (error) {
      toast.error('Error al cargar historial');
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setFilters({
      asset_id: 'all',
      start_date: '',
      end_date: '',
      tipo: 'all'
    });
  };

  const getTipoBadge = (tipo) => {
    const variants = {
      preventivo: 'bg-blue-50 text-blue-700 border-blue-200',
      correctivo: 'bg-orange-50 text-orange-700 border-orange-200',
      emergencia: 'bg-red-50 text-red-700 border-red-200'
    };
    const labels = {
      preventivo: 'Preventivo',
      correctivo: 'Correctivo',
      emergencia: 'Emergencia'
    };
    return (
      <span className={`${variants[tipo]} border rounded-full px-2.5 py-0.5 text-xs font-semibold`}>
        {labels[tipo]}
      </span>
    );
  };

  const exportToCSV = () => {
    if (maintenances.length === 0) {
      toast.error('No hay datos para exportar');
      return;
    }

    const headers = ['Fecha', 'Tipo', 'Activo', 'Sucursal', 'Costo', 'Descripción'];
    const rows = maintenances.map(m => [
      m.fecha_realizada || '',
      m.tipo || '',
      m.asset_details?.etiqueta_id || '',
      m.asset_details?.sucursal || '',
      m.costo || 0,
      m.descripcion || ''
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `historial_mantenimientos_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    toast.success('Reporte exportado');
  };

  const totalCost = maintenances.reduce((sum, m) => sum + (m.costo || 0), 0);

  return (
    <Layout>
      <div className="space-y-6" data-testid="reports-page">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight" style={{ fontFamily: 'Chivo, sans-serif' }}>
              Reportes
            </h1>
            <p className="mt-2 text-base text-slate-600">
              Historial de mantenimientos y reparaciones
            </p>
          </div>
          
          <Button 
            onClick={exportToCSV}
            disabled={maintenances.length === 0}
            className="mt-4 sm:mt-0 bg-emerald-600 hover:bg-emerald-700 text-white rounded-sm font-medium shadow-sm"
          >
            <Download className="h-4 w-4 mr-2" />
            Exportar CSV
          </Button>
        </div>

        {/* Filters */}
        <Card className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm">
          <div className="flex items-center mb-4">
            <Filter className="h-5 w-5 text-slate-600 mr-2" />
            <h2 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Chivo, sans-serif' }}>
              Filtros
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Activo</Label>
              <Select value={filters.asset_id} onValueChange={(value) => setFilters({ ...filters, asset_id: value })}>
                <SelectTrigger className="mt-1 bg-white border-slate-200 rounded-sm">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los activos</SelectItem>
                  {assets.map((asset) => (
                    <SelectItem key={asset.id} value={asset.id}>
                      {asset.etiqueta_id} - {asset.marca}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Tipo</Label>
              <Select value={filters.tipo} onValueChange={(value) => setFilters({ ...filters, tipo: value })}>
                <SelectTrigger className="mt-1 bg-white border-slate-200 rounded-sm">
                  <SelectValue placeholder="Todos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los tipos</SelectItem>
                  <SelectItem value="preventivo">Preventivo</SelectItem>
                  <SelectItem value="correctivo">Correctivo</SelectItem>
                  <SelectItem value="emergencia">Emergencia</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Desde</Label>
              <Input
                type="date"
                value={filters.start_date}
                onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
                className="mt-1 bg-white border-slate-200 rounded-sm"
              />
            </div>

            <div>
              <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Hasta</Label>
              <Input
                type="date"
                value={filters.end_date}
                onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
                className="mt-1 bg-white border-slate-200 rounded-sm"
              />
            </div>
          </div>

          <div className="flex justify-end mt-4">
            <Button variant="outline" onClick={clearFilters} className="rounded-sm">
              Limpiar Filtros
            </Button>
          </div>
        </Card>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Total Mantenimientos</p>
            <p className="text-3xl font-bold text-slate-900 mt-2">{maintenances.length}</p>
          </Card>
          <Card className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Costo Total</p>
            <p className="text-3xl font-bold text-slate-900 mt-2">
              ${totalCost.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
            </p>
          </Card>
          <Card className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Promedio por Mantenimiento</p>
            <p className="text-3xl font-bold text-slate-900 mt-2">
              ${maintenances.length > 0 ? (totalCost / maintenances.length).toLocaleString('es-MX', { minimumFractionDigits: 2 }) : '0.00'}
            </p>
          </Card>
        </div>

        {/* Maintenance List */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900"></div>
          </div>
        ) : maintenances.length === 0 ? (
          <Card className="p-12 bg-white border border-slate-200 shadow-sm rounded-sm text-center">
            <FileText className="h-16 w-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No se encontraron mantenimientos con los filtros aplicados</p>
          </Card>
        ) : (
          <Card className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-slate-200">
                  <tr>
                    <th className="text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-slate-600">Fecha</th>
                    <th className="text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-slate-600">Tipo</th>
                    <th className="text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-slate-600">Activo</th>
                    <th className="text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-slate-600">Sucursal</th>
                    <th className="text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-slate-600">Descripción</th>
                    <th className="text-right py-3 px-4 text-xs font-bold uppercase tracking-wider text-slate-600">Costo</th>
                  </tr>
                </thead>
                <tbody>
                  {maintenances.map((maintenance, index) => (
                    <tr key={maintenance.id || index} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-3 px-4 text-sm text-slate-900">
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 text-slate-400 mr-2" />
                          {maintenance.fecha_realizada ? new Date(maintenance.fecha_realizada).toLocaleDateString('es-MX') : 'N/A'}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        {getTipoBadge(maintenance.tipo)}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-900 font-mono">
                        {maintenance.asset_details?.etiqueta_id || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-700">
                        {maintenance.asset_details?.sucursal || 'N/A'}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-700">
                        {maintenance.descripcion || 'Sin descripción'}
                      </td>
                      <td className="py-3 px-4 text-sm font-semibold text-slate-900 text-right">
                        ${(maintenance.costo || 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default Reports;
