import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { getMaintenancePlans, createMaintenancePlan, getAssets } from '../utils/api';
import { Plus, Calendar, Trash2, Edit } from 'lucide-react';
import { toast } from 'sonner';

const MaintenancePlans = () => {
  const [plans, setPlans] = useState([]);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    tipo_agrupacion: 'individual',
    asset_ids: [],
    area_restaurante: '',
    sucursal: '',
    frecuencia_dias: 30,
    proximo_mantenimiento: '',
    notificar_dias_antes: 7,
    activo: true,
    notas: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [plansRes, assetsRes] = await Promise.all([
        getMaintenancePlans(),
        getAssets()
      ]);
      setPlans(plansRes.data);
      setAssets(assetsRes.data);
    } catch (error) {
      toast.error('Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createMaintenancePlan({
        ...formData,
        frecuencia_dias: parseInt(formData.frecuencia_dias),
        notificar_dias_antes: parseInt(formData.notificar_dias_antes)
      });
      toast.success('Plan de mantenimiento creado');
      setDialogOpen(false);
      fetchData();
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al crear plan');
    }
  };

  const resetForm = () => {
    setFormData({
      nombre: '',
      descripcion: '',
      tipo_agrupacion: 'individual',
      asset_ids: [],
      area_restaurante: '',
      sucursal: '',
      frecuencia_dias: 30,
      proximo_mantenimiento: '',
      notificar_dias_antes: 7,
      activo: true,
      notas: ''
    });
  };

  const getGroupingLabel = (plan) => {
    switch (plan.tipo_agrupacion) {
      case 'individual':
        return `${plan.asset_ids.length} activo(s)`;
      case 'area':
        return `Área: ${plan.area_restaurante}`;
      case 'sucursal':
        return `Sucursal: ${plan.sucursal}`;
      case 'selectivo':
        return `${plan.asset_ids.length} activos seleccionados`;
      default:
        return plan.tipo_agrupacion;
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

  return (
    <Layout>
      <div className="space-y-6" data-testid="maintenance-plans-page">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight" style={{ fontFamily: 'Chivo, sans-serif' }}>
              Planes de Mantenimiento
            </h1>
            <p className="mt-2 text-base text-slate-600">
              {plans.length} planes activos
            </p>
          </div>
          
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                className="mt-4 sm:mt-0 bg-slate-900 hover:bg-slate-800 text-white rounded-sm font-medium shadow-sm"
                data-testid="add-plan-button"
              >
                <Plus className="h-4 w-4 mr-2" />
                Nuevo Plan
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold" style={{ fontFamily: 'Chivo, sans-serif' }}>
                  Nuevo Plan de Mantenimiento
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Nombre del Plan *</Label>
                  <Input
                    required
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    className="mt-1 bg-white border-slate-200 rounded-sm"
                    placeholder="Ej: Mantenimiento Preventivo Mensual"
                  />
                </div>

                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Descripción</Label>
                  <Input
                    value={formData.descripcion}
                    onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                    className="mt-1 bg-white border-slate-200 rounded-sm"
                  />
                </div>

                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Tipo de Agrupación *</Label>
                  <Select 
                    value={formData.tipo_agrupacion} 
                    onValueChange={(value) => setFormData({ ...formData, tipo_agrupacion: value })}
                  >
                    <SelectTrigger className="mt-1 bg-white border-slate-200 rounded-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="individual">Individual</SelectItem>
                      <SelectItem value="area">Por Área</SelectItem>
                      <SelectItem value="sucursal">Por Sucursal</SelectItem>
                      <SelectItem value="selectivo">Selectivo (Múltiples)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {formData.tipo_agrupacion === 'area' && (
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Área del Restaurante *</Label>
                    <Input
                      required
                      value={formData.area_restaurante}
                      onChange={(e) => setFormData({ ...formData, area_restaurante: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                )}

                {formData.tipo_agrupacion === 'sucursal' && (
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Sucursal *</Label>
                    <Input
                      required
                      value={formData.sucursal}
                      onChange={(e) => setFormData({ ...formData, sucursal: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Frecuencia (días) *</Label>
                    <Input
                      type="number"
                      required
                      min="1"
                      value={formData.frecuencia_dias}
                      onChange={(e) => setFormData({ ...formData, frecuencia_dias: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Notificar antes (días)</Label>
                    <Input
                      type="number"
                      min="0"
                      value={formData.notificar_dias_antes}
                      onChange={(e) => setFormData({ ...formData, notificar_dias_antes: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                </div>

                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Próximo Mantenimiento *</Label>
                  <Input
                    type="date"
                    required
                    value={formData.proximo_mantenimiento}
                    onChange={(e) => setFormData({ ...formData, proximo_mantenimiento: e.target.value })}
                    className="mt-1 bg-white border-slate-200 rounded-sm"
                  />
                </div>

                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Notas</Label>
                  <Input
                    value={formData.notas}
                    onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
                    className="mt-1 bg-white border-slate-200 rounded-sm"
                  />
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} className="rounded-sm">
                    Cancelar
                  </Button>
                  <Button type="submit" className="bg-slate-900 hover:bg-slate-800 rounded-sm">
                    Crear Plan
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Plans Grid */}
        {plans.length === 0 ? (
          <Card className="p-12 bg-white border border-slate-200 shadow-sm rounded-sm text-center">
            <Calendar className="h-16 w-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No hay planes de mantenimiento creados</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {plans.map((plan) => (
              <Card 
                key={plan.id}
                className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm hover:border-slate-300 transition-colors"
                data-testid={`plan-card-${plan.id}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-slate-900">{plan.nombre}</h3>
                    <p className="text-sm text-slate-600 mt-1">{plan.descripcion}</p>
                  </div>
                  {plan.activo ? (
                    <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 border rounded-full px-2.5 py-0.5 text-xs font-semibold">
                      Activo
                    </Badge>
                  ) : (
                    <Badge className="bg-slate-100 text-slate-600 border-slate-200 border rounded-full px-2.5 py-0.5 text-xs font-semibold">
                      Inactivo
                    </Badge>
                  )}
                </div>

                <div className="space-y-3">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Agrupación</p>
                    <p className="text-sm text-slate-900">{getGroupingLabel(plan)}</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Frecuencia</p>
                    <p className="text-sm text-slate-900">Cada {plan.frecuencia_dias} días</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Próximo Mantenimiento</p>
                    <div className="flex items-center mt-1">
                      <Calendar className="h-4 w-4 text-slate-400 mr-2" />
                      <p className="text-sm text-slate-900">
                        {new Date(plan.proximo_mantenimiento).toLocaleDateString('es-MX')}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex space-x-2 mt-4 pt-4 border-t border-slate-100">
                  <Button variant="ghost" size="sm" className="flex-1">
                    <Edit className="h-4 w-4 mr-1" />
                    Editar
                  </Button>
                  <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700 hover:bg-red-50">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default MaintenancePlans;
