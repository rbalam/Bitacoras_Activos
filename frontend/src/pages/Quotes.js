import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { getQuotes, createQuote, getAssets, uploadFile } from '../utils/api';
import { Plus, FileText, AlertTriangle, CheckCircle, Upload, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Quotes = () => {
  const [quotes, setQuotes] = useState([]);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [quoteRequirement, setQuoteRequirement] = useState(null);
  const [formData, setFormData] = useState({
    asset_id: '',
    tipo_cotizacion: 'mantenimiento',
    proveedor: '',
    concepto: '',
    monto: '',
    validez_dias: 30,
    incluye: '',
    archivo_url: '',
    sistema_externo: '',
    pedido_externo_id: '',
    sucursal_sistema: '',
    notas: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [quotesRes, assetsRes] = await Promise.all([
        getQuotes(),
        getAssets()
      ]);
      setQuotes(quotesRes.data);
      setAssets(assetsRes.data);
    } catch (error) {
      toast.error('Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };

  const checkQuoteRequirement = async (assetId, monto) => {
    if (!assetId || !monto) return;
    
    try {
      const response = await axios.get(`${API}/quotes/check-requirement/${assetId}`, {
        params: { monto: parseFloat(monto) }
      });
      setQuoteRequirement(response.data);
      
      if (response.data.requires_multiple_quotes && response.data.existing_quotes === 0) {
        toast.info(`Monto ≥ $${response.data.threshold.toLocaleString()}: Se requieren mínimo 2 cotizaciones`, {
          duration: 5000
        });
      }
    } catch (error) {
      // Silently ignore to avoid exposing errors in production
    }
  };

  useEffect(() => {
    if (formData.asset_id && formData.monto) {
      checkQuoteRequirement(formData.asset_id, formData.monto);
    }
  }, [formData.asset_id, formData.monto]);

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      toast.error('Solo se permiten archivos PDF');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error('El archivo debe ser menor a 10MB');
      return;
    }

    setSelectedFile(file);
  };

  const uploadQuoteFile = async () => {
    if (!selectedFile) return null;

    setUploadingFile(true);
    try {
      const formDataFile = new FormData();
      formDataFile.append('file', selectedFile);
      formDataFile.append('entity_type', 'quote');
      formDataFile.append('entity_id', 'temp');

      const response = await uploadFile(formDataFile);
      toast.success('Archivo subido correctamente');
      return response.data.filename;
    } catch (error) {
      toast.error('Error al subir archivo');
      return null;
    } finally {
      setUploadingFile(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Upload file if selected
    let archivo_url = formData.archivo_url;
    if (selectedFile) {
      const filename = await uploadQuoteFile();
      if (filename) {
        archivo_url = `${BACKEND_URL}/api/download/${filename}`;
      }
    }

    try {
      await createQuote({
        ...formData,
        monto: parseFloat(formData.monto),
        validez_dias: parseInt(formData.validez_dias),
        archivo_url
      });
      
      toast.success('Cotización creada exitosamente');
      
      if (quoteRequirement?.requires_multiple_quotes && quoteRequirement.existing_quotes === 0) {
        toast.warning('Recuerda agregar una segunda cotización para cumplir con la política', {
          duration: 5000
        });
      }
      
      setDialogOpen(false);
      fetchData();
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al crear cotización');
    }
  };

  const resetForm = () => {
    setFormData({
      asset_id: '',
      tipo_cotizacion: 'mantenimiento',
      proveedor: '',
      concepto: '',
      monto: '',
      validez_dias: 30,
      incluye: '',
      archivo_url: '',
      sistema_externo: '',
      pedido_externo_id: '',
      sucursal_sistema: '',
      notas: ''
    });
    setSelectedFile(null);
    setQuoteRequirement(null);
  };

  const getTipoBadge = (tipo) => {
    const variants = {
      mantenimiento: 'bg-blue-50 text-blue-700 border-blue-200',
      refacciones: 'bg-purple-50 text-purple-700 border-purple-200'
    };
    const labels = {
      mantenimiento: 'Mantenimiento',
      refacciones: 'Refacciones'
    };
    return <Badge className={`${variants[tipo]} border rounded-full px-2.5 py-0.5 text-xs font-semibold`}>{labels[tipo]}</Badge>;
  };

  const getEstadoBadge = (estado) => {
    const variants = {
      pendiente: 'bg-orange-50 text-orange-700 border-orange-200',
      aprobada: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      rechazada: 'bg-red-50 text-red-700 border-red-200'
    };
    const labels = {
      pendiente: 'Pendiente',
      aprobada: 'Aprobada',
      rechazada: 'Rechazada'
    };
    return <Badge className={`${variants[estado]} border rounded-full px-2.5 py-0.5 text-xs font-semibold`}>{labels[estado]}</Badge>;
  };

  // Group quotes by asset_id for comparison
  const groupedQuotes = quotes.reduce((acc, quote) => {
    if (!acc[quote.asset_id]) {
      acc[quote.asset_id] = [];
    }
    acc[quote.asset_id].push(quote);
    return acc;
  }, {});

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
      <div className="space-y-6" data-testid="quotes-page">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight" style={{ fontFamily: 'Chivo, sans-serif' }}>
              Cotizaciones
            </h1>
            <p className="mt-2 text-base text-slate-600">
              {quotes.length} cotizaciones registradas
            </p>
          </div>
          
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                className="mt-4 sm:mt-0 bg-slate-900 hover:bg-slate-800 text-white rounded-sm font-medium shadow-sm"
                data-testid="add-quote-button"
              >
                <Plus className="h-4 w-4 mr-2" />
                Nueva Cotización
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold" style={{ fontFamily: 'Chivo, sans-serif' }}>
                  Nueva Cotización
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                {quoteRequirement?.requires_multiple_quotes && (
                  <Card className="p-4 bg-orange-50 border-orange-200 rounded-sm">
                    <div className="flex">
                      <AlertTriangle className="h-5 w-5 text-orange-600 mr-3 mt-0.5" />
                      <div>
                        <p className="text-sm font-semibold text-orange-900">Múltiples Cotizaciones Requeridas</p>
                        <p className="text-sm text-orange-800 mt-1">
                          {quoteRequirement.message}
                        </p>
                      </div>
                    </div>
                  </Card>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Activo *</Label>
                    <Select required value={formData.asset_id} onValueChange={(value) => setFormData({ ...formData, asset_id: value })}>
                      <SelectTrigger className="mt-1 bg-white border-slate-200 rounded-sm">
                        <SelectValue placeholder="Seleccionar activo" />
                      </SelectTrigger>
                      <SelectContent>
                        {assets.map((asset) => (
                          <SelectItem key={asset.id} value={asset.id}>
                            {asset.etiqueta_id} - {asset.marca} {asset.modelo}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Tipo *</Label>
                    <Select value={formData.tipo_cotizacion} onValueChange={(value) => setFormData({ ...formData, tipo_cotizacion: value })}>
                      <SelectTrigger className="mt-1 bg-white border-slate-200 rounded-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="mantenimiento">Mantenimiento</SelectItem>
                        <SelectItem value="refacciones">Refacciones</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Proveedor *</Label>
                    <Input
                      required
                      value={formData.proveedor}
                      onChange={(e) => setFormData({ ...formData, proveedor: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>

                  <div>
                    <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Monto *</Label>
                    <Input
                      type="number"
                      step="0.01"
                      required
                      value={formData.monto}
                      onChange={(e) => setFormData({ ...formData, monto: e.target.value })}
                      className="mt-1 bg-white border-slate-200 rounded-sm"
                    />
                  </div>
                </div>

                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Concepto *</Label>
                  <Input
                    required
                    value={formData.concepto}
                    onChange={(e) => setFormData({ ...formData, concepto: e.target.value })}
                    className="mt-1 bg-white border-slate-200 rounded-sm"
                  />
                </div>

                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Incluye</Label>
                  <Input
                    value={formData.incluye}
                    onChange={(e) => setFormData({ ...formData, incluye: e.target.value })}
                    className="mt-1 bg-white border-slate-200 rounded-sm"
                    placeholder="Ej: Mano de obra, refacciones, garantía"
                  />
                </div>

                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Archivo PDF</Label>
                  <div className="mt-1">
                    <Input
                      type="file"
                      accept=".pdf"
                      onChange={handleFileSelect}
                      className="bg-white border-slate-200 rounded-sm"
                    />
                    {selectedFile && (
                      <p className="text-xs text-emerald-600 mt-1 flex items-center">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        {selectedFile.name}
                      </p>
                    )}
                  </div>
                </div>

                <div className="border-t border-slate-200 pt-4">
                  <h3 className="text-sm font-bold text-slate-900 mb-3">Relación con Sistema Externo (Opcional)</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Sistema</Label>
                      <Select value={formData.sistema_externo} onValueChange={(value) => setFormData({ ...formData, sistema_externo: value })}>
                        <SelectTrigger className="mt-1 bg-white border-slate-200 rounded-sm">
                          <SelectValue placeholder="Ninguno" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">Ninguno</SelectItem>
                          <SelectItem value="mpro">MPRO</SelectItem>
                          <SelectItem value="soft">Softrestaurant</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">ID Pedido</Label>
                      <Input
                        value={formData.pedido_externo_id}
                        onChange={(e) => setFormData({ ...formData, pedido_externo_id: e.target.value })}
                        className="mt-1 bg-white border-slate-200 rounded-sm"
                        placeholder="Ej: PED-12345"
                      />
                    </div>

                    <div>
                      <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Sucursal</Label>
                      <Input
                        value={formData.sucursal_sistema}
                        onChange={(e) => setFormData({ ...formData, sucursal_sistema: e.target.value })}
                        className="mt-1 bg-white border-slate-200 rounded-sm"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} className="rounded-sm">
                    Cancelar
                  </Button>
                  <Button type="submit" disabled={uploadingFile} className="bg-slate-900 hover:bg-slate-800 rounded-sm">
                    {uploadingFile ? 'Subiendo...' : 'Crear Cotización'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Grouped Quotes with Comparison */}
        {Object.entries(groupedQuotes).map(([assetId, assetQuotes]) => {
          const asset = assets.find(a => a.id === assetId);
          const hasMultiple = assetQuotes.length > 1;
          const lowestQuote = hasMultiple ? assetQuotes.reduce((min, q) => q.monto < min.monto ? q : min) : null;

          return (
            <Card key={assetId} className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-slate-900" style={{ fontFamily: 'Chivo, sans-serif' }}>
                    {asset?.etiqueta_id} - {asset?.marca} {asset?.modelo}
                  </h3>
                  <p className="text-sm text-slate-600">{asset?.sucursal}</p>
                </div>
                {hasMultiple && (
                  <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 border rounded-full px-3 py-1">
                    {assetQuotes.length} Cotizaciones
                  </Badge>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {assetQuotes.map((quote) => (
                  <Card 
                    key={quote.id}
                    className={`p-4 ${quote.id === lowestQuote?.id ? 'border-2 border-emerald-500 bg-emerald-50/30' : 'border border-slate-200'} rounded-sm relative`}
                  >
                    {quote.id === lowestQuote?.id && (
                      <div className="absolute -top-2 -right-2">
                        <Badge className="bg-emerald-600 text-white">Menor Precio</Badge>
                      </div>
                    )}
                    
                    <div className="flex items-start justify-between mb-3">
                      {getTipoBadge(quote.tipo_cotizacion)}
                      {getEstadoBadge(quote.estado)}
                    </div>

                    <div className="space-y-2">
                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Proveedor</p>
                        <p className="text-sm font-semibold text-slate-900">{quote.proveedor}</p>
                      </div>

                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Concepto</p>
                        <p className="text-sm text-slate-700">{quote.concepto}</p>
                      </div>

                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Monto</p>
                        <p className="text-2xl font-bold text-slate-900">
                          ${quote.monto.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                        </p>
                      </div>

                      {quote.incluye && (
                        <div>
                          <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Incluye</p>
                          <p className="text-xs text-slate-600">{quote.incluye}</p>
                        </div>
                      )}

                      {quote.sistema_externo && (
                        <div className="pt-2 border-t border-slate-200">
                          <p className="text-xs text-slate-600 flex items-center">
                            <ExternalLink className="h-3 w-3 mr-1" />
                            {quote.sistema_externo.toUpperCase()}: {quote.pedido_externo_id}
                          </p>
                        </div>
                      )}

                      {quote.archivo_url && (
                        <a 
                          href={quote.archivo_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="flex items-center text-sm text-blue-600 hover:text-blue-700 mt-2"
                        >
                          <FileText className="h-4 w-4 mr-1" />
                          Ver PDF
                        </a>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </Card>
          );
        })}

        {quotes.length === 0 && (
          <Card className="p-12 bg-white border border-slate-200 shadow-sm rounded-sm text-center">
            <FileText className="h-16 w-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No hay cotizaciones registradas</p>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default Quotes;
