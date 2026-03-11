import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { getAssets, createAsset } from '../utils/api';
import { Plus, Search, Package, MapPin, Calendar } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const Inventory = () => {
  const navigate = useNavigate();
  const [assets, setAssets] = useState([]);
  const [filteredAssets, setFilteredAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterEstado, setFilterEstado] = useState('all');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    serial_number: '',
    etiqueta_id: '',
    modelo: '',
    marca: '',
    capacidad: '',
    area_restaurante: '',
    sucursal: '',
    ubicacion_especifica: '',
    costo_equipo: '',
    fecha_compra: '',
    estado: 'operativo',
    notas: ''
  });

  useEffect(() => {
    fetchAssets();
  }, []);

  useEffect(() => {
    filterAssets();
  }, [searchTerm, filterEstado, assets]);

  const fetchAssets = async () => {
    try {
      const response = await getAssets();
      setAssets(response.data);
      setFilteredAssets(response.data);
    } catch (error) {
      toast.error('Error al cargar inventario');
    } finally {
      setLoading(false);
    }
  };

  const filterAssets = () => {
    let filtered = assets;

    if (searchTerm) {
      filtered = filtered.filter(asset => 
        asset.serial_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        asset.etiqueta_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        asset.modelo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        asset.marca.toLowerCase().includes(searchTerm.toLowerCase()) ||
        asset.sucursal.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterEstado !== 'all') {
      filtered = filtered.filter(asset => asset.estado === filterEstado);
    }

    setFilteredAssets(filtered);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createAsset({
        ...formData,
        costo_equipo: parseFloat(formData.costo_equipo)
      });
      toast.success('Activo creado exitosamente');
      setDialogOpen(false);
      fetchAssets();
      setFormData({
        serial_number: '',
        etiqueta_id: '',
        modelo: '',
        marca: '',
        capacidad: '',
        area_restaurante: '',
        sucursal: '',
        ubicacion_especifica: '',
        costo_equipo: '',
        fecha_compra: '',
        estado: 'operativo',
        notas: ''
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al crear activo');
    }
  };

  const getEstadoBadge = (estado) => {
    const variants = {
      operativo: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      mantenimiento: 'bg-blue-50 text-blue-700 border-blue-200',
      critico: 'bg-red-50 text-red-700 border-red-200',
      dado_de_baja: 'bg-slate-50 text-slate-700 border-slate-200'
    };
    const labels = {
      operativo: 'Operativo',
      mantenimiento: 'Mantenimiento',
      critico: 'Crítico',
      dado_de_baja: 'Dado de Baja'
    };
    return <Badge className={`${variants[estado]} border rounded-full px-2.5 py-0.5 text-xs font-semibold`}>{labels[estado]}</Badge>;
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
      <div className="space-y-6" data-testid="inventory-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight" style={{ fontFamily: 'Chivo, sans-serif' }}>
              Inventario
            </h1>
            <p className="mt-2 text-base text-slate-600">
              {filteredAssets.length} activos registrados
            </p>
          </div>
          
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                className="mt-4 sm:mt-0 bg-slate-900 hover:bg-slate-800 text-white rounded-sm font-medium shadow-sm"
                data-testid="add-asset-button"
              >
                <Plus className="h-4 w-4 mr-2" />
                Agregar Activo
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold" style={{ fontFamily: 'Chivo, sans-serif' }}>
                  Nuevo Aire Acondicionado
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Número de Serie *</Label>
                    <Input
                      required
                      data-testid="serial-number-input"
                      value={formData.serial_number}
                      onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Etiqueta/Placa ID *</Label>
                    <Input
                      required
                      data-testid="etiqueta-input"
                      value={formData.etiqueta_id}
                      onChange={(e) => setFormData({ ...formData, etiqueta_id: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Marca *</Label>
                    <Input
                      required
                      data-testid="marca-input"
                      value={formData.marca}
                      onChange={(e) => setFormData({ ...formData, marca: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Modelo *</Label>
                    <Input
                      required
                      data-testid="modelo-input"
                      value={formData.modelo}
                      onChange={(e) => setFormData({ ...formData, modelo: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Capacidad *</Label>
                    <Input
                      required
                      data-testid="capacidad-input"
                      placeholder="ej: 24000 BTU"
                      value={formData.capacidad}
                      onChange={(e) => setFormData({ ...formData, capacidad: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Costo del Equipo *</Label>
                    <Input
                      required
                      type="number"
                      step="0.01"
                      data-testid="costo-input"
                      value={formData.costo_equipo}
                      onChange={(e) => setFormData({ ...formData, costo_equipo: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Sucursal *</Label>
                    <Input
                      required
                      data-testid="sucursal-input"
                      value={formData.sucursal}
                      onChange={(e) => setFormData({ ...formData, sucursal: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Área *</Label>
                    <Input
                      required
                      data-testid="area-input"
                      placeholder="ej: Comedor Principal"
                      value={formData.area_restaurante}
                      onChange={(e) => setFormData({ ...formData, area_restaurante: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Ubicación Específica</Label>
                    <Input
                      data-testid="ubicacion-input"
                      value={formData.ubicacion_especifica}
                      onChange={(e) => setFormData({ ...formData, ubicacion_especifica: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Fecha de Compra</Label>
                    <Input
                      type="date"
                      data-testid="fecha-compra-input"
                      value={formData.fecha_compra}
                      onChange={(e) => setFormData({ ...formData, fecha_compra: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                </div>
                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Notas</Label>
                  <Input
                    data-testid="notas-input"
                    value={formData.notas}
                    onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
                    className="mt-1 bg-white border-slate-200 rounded-sm"
                  />
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} className="rounded-sm">
                    Cancelar
                  </Button>
                  <Button type="submit" className="bg-slate-900 hover:bg-slate-800 rounded-sm" data-testid="submit-asset-button">
                    Crear Activo
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Filters */}
        <Card className="p-4 bg-white border border-slate-200 shadow-sm rounded-sm">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <Input
                placeholder="Buscar por serie, etiqueta, modelo, marca o sucursal..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                data-testid="search-input"
                className="pl-10 bg-white border-slate-200 rounded-sm"
              />
            </div>
            <Select value={filterEstado} onValueChange={setFilterEstado}>
              <SelectTrigger className="w-full sm:w-48 bg-white border-slate-200 rounded-sm" data-testid="filter-estado">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los Estados</SelectItem>
                <SelectItem value="operativo">Operativo</SelectItem>
                <SelectItem value="mantenimiento">Mantenimiento</SelectItem>
                <SelectItem value="critico">Crítico</SelectItem>
                <SelectItem value="dado_de_baja">Dado de Baja</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </Card>

        {/* Assets Grid */}
        {filteredAssets.length === 0 ? (
          <Card className="p-12 bg-white border border-slate-200 shadow-sm rounded-sm text-center">
            <Package className="h-16 w-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No se encontraron activos</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredAssets.map((asset) => (
              <Card 
                key={asset.id}
                className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm hover:border-slate-300 transition-colors cursor-pointer"
                onClick={() => navigate(`/asset/${asset.id}`)}
                data-testid={`asset-card-${asset.id}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <Package className="h-5 w-5 text-slate-400 mr-2" />
                      <span className="font-mono text-sm font-semibold text-slate-900">{asset.etiqueta_id}</span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1 font-mono">{asset.serial_number}</p>
                  </div>
                  {getEstadoBadge(asset.estado)}
                </div>

                <div className="space-y-2">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Marca & Modelo</p>
                    <p className="text-sm font-semibold text-slate-900">{asset.marca} {asset.modelo}</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Capacidad</p>
                    <p className="text-sm text-slate-700">{asset.capacidad}</p>
                  </div>
                  <div className="flex items-center text-sm text-slate-600">
                    <MapPin className="h-4 w-4 mr-1 text-slate-400" />
                    {asset.sucursal} - {asset.area_restaurante}
                  </div>
                  {asset.ultimo_mantenimiento && (
                    <div className="flex items-center text-xs text-slate-500 pt-2 border-t border-slate-100">
                      <Calendar className="h-3 w-3 mr-1" />
                      Último mtto: {new Date(asset.ultimo_mantenimiento).toLocaleDateString('es-MX')}
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Inventory;
