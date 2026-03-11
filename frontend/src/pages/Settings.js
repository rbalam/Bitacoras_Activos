import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Switch } from '../components/ui/switch';
import axios from 'axios';
import { toast } from 'sonner';
import { Settings, Eye, EyeOff, Edit, TestTube, Save, AlertCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ConfigSettings = () => {
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingConfig, setEditingConfig] = useState(null);
  const [showValue, setShowValue] = useState({});
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [testData, setTestData] = useState({ email: '', phone: '' });
  const [formData, setFormData] = useState({ value: '', description: '', active: true });

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      const response = await axios.get(`${API}/config`);
      setConfigs(response.data);
    } catch (error) {
      toast.error('Error al cargar configuraciones');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = async (config) => {
    try {
      // Get full config details (with unmasked value)
      const response = await axios.get(`${API}/config/${config.id}`);
      setEditingConfig(response.data);
      setFormData({
        value: response.data.value,
        description: response.data.description || '',
        active: response.data.active
      });
      setEditDialogOpen(true);
    } catch (error) {
      toast.error('Error al cargar configuración');
    }
  };

  const handleSave = async () => {
    try {
      await axios.put(`${API}/config/${editingConfig.id}`, formData);
      toast.success('Configuración actualizada exitosamente');
      setEditDialogOpen(false);
      fetchConfigs();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al actualizar configuración');
    }
  };

  const handleTestNotification = async () => {
    try {
      const response = await axios.post(`${API}/config/test-notification`, {
        test_email: testData.email,
        test_phone: testData.phone || null
      });
      
      const results = response.data.results;
      if (results.email) {
        toast.success('✓ Email enviado correctamente');
      } else {
        toast.error('✗ Error al enviar email');
      }
      
      if (testData.phone) {
        if (results.whatsapp) {
          toast.success('✓ WhatsApp enviado correctamente');
        } else {
          toast.error('✗ Error al enviar WhatsApp');
        }
      }
      
      setTestDialogOpen(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al enviar notificación de prueba');
    }
  };

  const getCategoryBadge = (category) => {
    const variants = {
      twilio: 'bg-green-50 text-green-700 border-green-200',
      email: 'bg-blue-50 text-blue-700 border-blue-200',
      sql_server: 'bg-purple-50 text-purple-700 border-purple-200',
      general: 'bg-slate-50 text-slate-700 border-slate-200'
    };
    const labels = {
      twilio: 'Twilio',
      email: 'Email',
      sql_server: 'SQL Server',
      general: 'General'
    };
    return <Badge className={`${variants[category]} border rounded-full px-2.5 py-0.5 text-xs font-semibold`}>{labels[category]}</Badge>;
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
      <div className="space-y-6" data-testid="settings-page">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight" style={{ fontFamily: 'Chivo, sans-serif' }}>
              Configuración
            </h1>
            <p className="mt-2 text-base text-slate-600">
              Gestión de credenciales y servicios externos
            </p>
          </div>
          
          <Button 
            onClick={() => setTestDialogOpen(true)}
            className="mt-4 sm:mt-0 bg-emerald-600 hover:bg-emerald-700 text-white rounded-sm font-medium shadow-sm"
            data-testid="test-notification-button"
          >
            <TestTube className="h-4 w-4 mr-2" />
            Probar Notificaciones
          </Button>
        </div>

        {/* Alert */}
        <Card className="p-4 bg-blue-50 border-blue-200 rounded-sm">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-blue-600 mr-3 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-blue-900">Información de Seguridad</p>
              <p className="text-sm text-blue-800 mt-1">
                Las credenciales sensibles están encriptadas y solo son visibles para administradores. 
                Los cambios se aplican inmediatamente sin necesidad de reiniciar el servidor.
              </p>
            </div>
          </div>
        </Card>

        {/* Configurations List */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {configs.map((config) => (
            <Card 
              key={config.id}
              className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm hover:border-slate-300 transition-colors"
              data-testid={`config-card-${config.key}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    {getCategoryBadge(config.category)}
                    {!config.active && (
                      <Badge className="bg-slate-100 text-slate-600 border-slate-200 border rounded-full px-2.5 py-0.5 text-xs font-semibold">
                        Inactivo
                      </Badge>
                    )}
                  </div>
                  <p className="font-mono text-sm font-semibold text-slate-900">{config.key}</p>
                  {config.description && (
                    <p className="text-xs text-slate-500 mt-1">{config.description}</p>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEdit(config)}
                  data-testid={`edit-${config.key}`}
                >
                  <Edit className="h-4 w-4" />
                </Button>
              </div>

              <div className="mt-4">
                <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Valor</Label>
                <div className="mt-2 flex items-center">
                  {config.is_sensitive ? (
                    <div className="flex-1 flex items-center space-x-2">
                      <Input
                        type={showValue[config.id] ? "text" : "password"}
                        value={config.value}
                        readOnly
                        className="bg-slate-50 border-slate-200 rounded-sm font-mono text-sm"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowValue({ ...showValue, [config.id]: !showValue[config.id] })}
                      >
                        {showValue[config.id] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  ) : (
                    <Input
                      value={config.value}
                      readOnly
                      className="bg-slate-50 border-slate-200 rounded-sm font-mono text-sm"
                    />
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Edit Dialog */}
        <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold" style={{ fontFamily: 'Chivo, sans-serif' }}>
                Editar Configuración
              </DialogTitle>
            </DialogHeader>
            {editingConfig && (
              <div className="space-y-4">
                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Clave</Label>
                  <Input
                    value={editingConfig.key}
                    readOnly
                    className="mt-1 bg-slate-50 border-slate-200 rounded-sm font-mono"
                  />
                </div>
                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Valor *</Label>
                  <Input
                    type={editingConfig.is_sensitive ? "password" : "text"}
                    value={formData.value}
                    onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                    className="mt-1 bg-white border-slate-200 rounded-sm font-mono"
                    data-testid="config-value-input"
                  />
                </div>
                <div>
                  <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Descripción</Label>
                  <Input
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="mt-1 bg-white border-slate-200 rounded-sm"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={formData.active}
                    onCheckedChange={(checked) => setFormData({ ...formData, active: checked })}
                    data-testid="config-active-switch"
                  />
                  <Label className="text-sm font-medium text-slate-700">Configuración activa</Label>
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <Button variant="outline" onClick={() => setEditDialogOpen(false)} className="rounded-sm">
                    Cancelar
                  </Button>
                  <Button onClick={handleSave} className="bg-slate-900 hover:bg-slate-800 rounded-sm" data-testid="save-config-button">
                    <Save className="h-4 w-4 mr-2" />
                    Guardar
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Test Notification Dialog */}
        <Dialog open={testDialogOpen} onOpenChange={setTestDialogOpen}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold" style={{ fontFamily: 'Chivo, sans-serif' }}>
                Probar Notificaciones
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <p className="text-sm text-slate-600">
                Envía una notificación de prueba para verificar que las configuraciones funcionan correctamente.
              </p>
              <div>
                <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Email de Prueba *</Label>
                <Input
                  type="email"
                  value={testData.email}
                  onChange={(e) => setTestData({ ...testData, email: e.target.value })}
                  className="mt-1 bg-white border-slate-200 rounded-sm"
                  placeholder="tu@email.com"
                  data-testid="test-email-input"
                />
              </div>
              <div>
                <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">Teléfono WhatsApp (Opcional)</Label>
                <Input
                  type="tel"
                  value={testData.phone}
                  onChange={(e) => setTestData({ ...testData, phone: e.target.value })}
                  className="mt-1 bg-white border-slate-200 rounded-sm"
                  placeholder="+521234567890"
                  data-testid="test-phone-input"
                />
                <p className="text-xs text-slate-500 mt-1">Formato: +[código país][número]</p>
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <Button variant="outline" onClick={() => setTestDialogOpen(false)} className="rounded-sm">
                  Cancelar
                </Button>
                <Button 
                  onClick={handleTestNotification} 
                  className="bg-emerald-600 hover:bg-emerald-700 rounded-sm"
                  disabled={!testData.email}
                  data-testid="send-test-button"
                >
                  <TestTube className="h-4 w-4 mr-2" />
                  Enviar Prueba
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

export default ConfigSettings;
