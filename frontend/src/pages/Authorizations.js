import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Switch } from '../components/ui/switch';
import { getAuthorizations, approveAuthorization, rejectAuthorization } from '../utils/api';
import { CheckCircle, XCircle, Clock, MessageSquare } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';

const Authorizations = () => {
  const { user } = useAuth();
  const [authorizations, setAuthorizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionDialog, setActionDialog] = useState(false);
  const [selectedAuth, setSelectedAuth] = useState(null);
  const [actionType, setActionType] = useState(null);
  const [comentarios, setComentarios] = useState('');
  const [notifyWhatsApp, setNotifyWhatsApp] = useState(true);

  useEffect(() => {
    fetchAuthorizations();
  }, []);

  const fetchAuthorizations = async () => {
    try {
      const response = await getAuthorizations();
      setAuthorizations(response.data);
    } catch (error) {
      toast.error('Error al cargar autorizaciones');
    } finally {
      setLoading(false);
    }
  };

  const openActionDialog = (auth, type) => {
    setSelectedAuth(auth);
    setActionType(type);
    setComentarios('');
    setNotifyWhatsApp(true);
    setActionDialog(true);
  };

  const handleAction = async () => {
    try {
      if (actionType === 'approve') {
        await approveAuthorization(selectedAuth.id, comentarios, notifyWhatsApp);
        toast.success('Autorización aprobada');
      } else {
        if (!comentarios) {
          toast.error('El motivo de rechazo es obligatorio');
          return;
        }
        await rejectAuthorization(selectedAuth.id, comentarios, notifyWhatsApp);
        toast.success('Autorización rechazada');
      }
      setActionDialog(false);
      fetchAuthorizations();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al procesar autorización');
    }
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
    return (
      <Badge className={`${variants[estado]} border rounded-full px-2.5 py-0.5 text-xs font-semibold`}>
        {labels[estado]}
      </Badge>
    );
  };

  const getTipoBadge = (tipo) => {
    const labels = {
      mantenimiento: 'Mantenimiento',
      compra: 'Compra',
      baja_equipo: 'Baja de Equipo',
      sustitucion: 'Sustitución'
    };
    return labels[tipo] || tipo;
  };

  const canApprove = user?.role === 'admin' || user?.role === 'gerente';

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900"></div>
        </div>
      </Layout>
    );
  }

  const pendientes = authorizations.filter(a => a.estado === 'pendiente');
  const procesadas = authorizations.filter(a => a.estado !== 'pendiente');

  return (
    <Layout>
      <div className="space-y-6" data-testid="authorizations-page">
        <div>
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight" style={{ fontFamily: 'Chivo, sans-serif' }}>
            Autorizaciones
          </h1>
          <p className="mt-2 text-base text-slate-600">
            {pendientes.length} pendientes de aprobación
          </p>
        </div>

        {/* Pendientes */}
        {pendientes.length > 0 && (
          <div>
            <h2 className="text-xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Chivo, sans-serif' }}>
              Pendientes de Aprobación
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {pendientes.map((auth) => (
                <Card 
                  key={auth.id}
                  className="p-6 bg-white border border-orange-200 shadow-sm rounded-sm"
                  data-testid={`auth-card-${auth.id}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Badge className="bg-blue-50 text-blue-700 border-blue-200 border rounded-full px-2.5 py-0.5 text-xs font-semibold">
                          {getTipoBadge(auth.tipo)}
                        </Badge>
                        {getEstadoBadge(auth.estado)}
                      </div>
                      <p className="text-sm font-semibold text-slate-900">{auth.justificacion}</p>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    {auth.monto && (
                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Monto</p>
                        <p className="text-lg font-bold text-slate-900">
                          ${auth.monto.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                        </p>
                      </div>
                    )}
                    <div>
                      <p className="text-xs font-bold uppercase tracking-wider text-slate-600">Solicitado</p>
                      <p className="text-sm text-slate-700">
                        {new Date(auth.created_at).toLocaleDateString('es-MX', { 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}
                      </p>
                    </div>
                  </div>

                  {canApprove && (
                    <div className="flex space-x-2 pt-4 border-t border-slate-100">
                      <Button
                        onClick={() => openActionDialog(auth, 'approve')}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-sm"
                        data-testid={`approve-${auth.id}`}
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Aprobar
                      </Button>
                      <Button
                        onClick={() => openActionDialog(auth, 'reject')}
                        variant="outline"
                        className="flex-1 border-red-200 text-red-600 hover:bg-red-50 rounded-sm"
                        data-testid={`reject-${auth.id}`}
                      >
                        <XCircle className="h-4 w-4 mr-2" />
                        Rechazar
                      </Button>
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Procesadas */}
        {procesadas.length > 0 && (
          <div>
            <h2 className="text-xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Chivo, sans-serif' }}>
              Historial
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {procesadas.map((auth) => (
                <Card 
                  key={auth.id}
                  className="p-6 bg-white border border-slate-200 shadow-sm rounded-sm"
                >
                  <div className="flex items-start justify-between mb-3">
                    <Badge className="bg-blue-50 text-blue-700 border-blue-200 border rounded-full px-2.5 py-0.5 text-xs font-semibold">
                      {getTipoBadge(auth.tipo)}
                    </Badge>
                    {getEstadoBadge(auth.estado)}
                  </div>

                  <p className="text-sm text-slate-900 mb-3">{auth.justificacion}</p>

                  {auth.monto && (
                    <p className="text-lg font-bold text-slate-900 mb-2">
                      ${auth.monto.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                    </p>
                  )}

                  {auth.comentarios && (
                    <div className="mt-3 p-3 bg-slate-50 rounded-sm">
                      <p className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">Comentarios</p>
                      <p className="text-sm text-slate-700">{auth.comentarios}</p>
                    </div>
                  )}

                  <p className="text-xs text-slate-500 mt-3">
                    {auth.fecha_resolucion && `Procesado: ${new Date(auth.fecha_resolucion).toLocaleDateString('es-MX')}`}
                  </p>
                </Card>
              ))}
            </div>
          </div>
        )}

        {authorizations.length === 0 && (
          <Card className="p-12 bg-white border border-slate-200 shadow-sm rounded-sm text-center">
            <Clock className="h-16 w-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No hay autorizaciones registradas</p>
          </Card>
        )}

        {/* Action Dialog */}
        <Dialog open={actionDialog} onOpenChange={setActionDialog}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold" style={{ fontFamily: 'Chivo, sans-serif' }}>
                {actionType === 'approve' ? 'Aprobar Autorización' : 'Rechazar Autorización'}
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label className="text-xs font-bold uppercase tracking-wider text-slate-600">
                  {actionType === 'approve' ? 'Comentarios (Opcional)' : 'Motivo de Rechazo *'}
                </Label>
                <Input
                  value={comentarios}
                  onChange={(e) => setComentarios(e.target.value)}
                  className="mt-1 bg-white border-slate-200 rounded-sm"
                  placeholder={actionType === 'approve' ? 'Agregar comentarios...' : 'Especifica el motivo del rechazo'}
                  required={actionType === 'reject'}
                />
              </div>

              <div className="flex items-center space-x-2 p-4 bg-slate-50 rounded-sm">
                <MessageSquare className="h-5 w-5 text-slate-600" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-900">Notificar por WhatsApp</p>
                  <p className="text-xs text-slate-600">Enviar notificación al solicitante</p>
                </div>
                <Switch
                  checked={notifyWhatsApp}
                  onCheckedChange={setNotifyWhatsApp}
                  data-testid="notify-whatsapp-switch"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <Button variant="outline" onClick={() => setActionDialog(false)} className="rounded-sm">
                  Cancelar
                </Button>
                <Button 
                  onClick={handleAction}
                  className={actionType === 'approve' ? 'bg-emerald-600 hover:bg-emerald-700 rounded-sm' : 'bg-red-600 hover:bg-red-700 rounded-sm'}
                  data-testid="confirm-action-button"
                >
                  {actionType === 'approve' ? 'Aprobar' : 'Rechazar'}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

export default Authorizations;
