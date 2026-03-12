import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card } from '../components/ui/card';
import { toast } from 'sonner';
import axios from 'axios';
import { ArrowLeft, Lock, Mail, Eye, EyeOff } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ForgotPassword = () => {
  const [step, setStep] = useState(1); // 1: request, 2: confirm
  const [email, setEmail] = useState('');
  const [resetCode, setResetCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/reset-password-request`, null, {
        params: { email }
      });
      
      // En desarrollo, mostramos el código generado
      if (response.data.reset_code) {
        setGeneratedCode(response.data.reset_code);
        toast.success(`Código generado: ${response.data.reset_code}`, { duration: 10000 });
      }
      
      toast.info('Código de reseteo generado. Válido por 15 minutos.');
      setStep(2);
    } catch (error) {
      toast.error('Error al solicitar reseteo de contraseña');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmReset = async (e) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      toast.error('Las contraseñas no coinciden');
      return;
    }

    if (newPassword.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API}/auth/reset-password-confirm`, null, {
        params: {
          email,
          reset_code: resetCode,
          new_password: newPassword
        }
      });
      
      toast.success('¡Contraseña actualizada exitosamente!');
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error al cambiar contraseña');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-slate-50" data-testid="forgot-password-page">
      <Card className="w-full max-w-md p-8 bg-white border border-slate-200 shadow-sm rounded-sm">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Chivo, sans-serif' }}>
            Restablecer Contraseña
          </h2>
          <p className="text-slate-600">
            {step === 1 
              ? 'Ingresa tu email para recibir un código de reseteo'
              : 'Ingresa el código recibido y tu nueva contraseña'
            }
          </p>
        </div>

        {step === 1 ? (
          <form onSubmit={handleRequestReset} className="space-y-6">
            <div>
              <Label htmlFor="email" className="text-sm font-bold uppercase tracking-wider text-slate-600">
                Email
              </Label>
              <div className="mt-2 relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
                <Input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 bg-white border-slate-200 focus:ring-2 focus:ring-slate-900/10 rounded-sm"
                  placeholder="tu@email.com"
                  data-testid="email-input"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-sm font-medium shadow-sm"
              data-testid="request-reset-button"
            >
              {loading ? 'Procesando...' : 'Solicitar Código'}
            </Button>
          </form>
        ) : (
          <form onSubmit={handleConfirmReset} className="space-y-6">
            {generatedCode && (
              <Card className="p-4 bg-blue-50 border-blue-200 rounded-sm">
                <p className="text-sm font-semibold text-blue-900">Código Generado (Solo para desarrollo)</p>
                <p className="text-2xl font-bold text-blue-700 mt-2 font-mono tracking-wider">{generatedCode}</p>
                <p className="text-xs text-blue-600 mt-2">Válido por 15 minutos</p>
              </Card>
            )}

            <div>
              <Label className="text-sm font-bold uppercase tracking-wider text-slate-600">
                Código de Reseteo
              </Label>
              <Input
                type="text"
                required
                value={resetCode}
                onChange={(e) => setResetCode(e.target.value)}
                className="mt-2 bg-white border-slate-200 rounded-sm font-mono text-lg tracking-wider"
                placeholder="123456"
                maxLength={6}
                data-testid="reset-code-input"
              />
            </div>

            <div>
              <Label className="text-sm font-bold uppercase tracking-wider text-slate-600">
                Nueva Contraseña
              </Label>
              <div className="mt-2 relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
                <Input
                  type={showNewPassword ? "text" : "password"}
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="pl-10 pr-10 bg-white border-slate-200 rounded-sm"
                  placeholder="••••••••"
                  data-testid="new-password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showNewPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <div>
              <Label className="text-sm font-bold uppercase tracking-wider text-slate-600">
                Confirmar Contraseña
              </Label>
              <div className="mt-2 relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
                <Input
                  type={showConfirmPassword ? "text" : "password"}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="pl-10 pr-10 bg-white border-slate-200 rounded-sm"
                  placeholder="••••••••"
                  data-testid="confirm-password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-sm font-medium shadow-sm"
              data-testid="confirm-reset-button"
            >
              {loading ? 'Actualizando...' : 'Cambiar Contraseña'}
            </Button>

            <Button
              type="button"
              variant="outline"
              onClick={() => setStep(1)}
              className="w-full rounded-sm"
            >
              Solicitar Nuevo Código
            </Button>
          </form>
        )}

        <div className="mt-6 text-center">
          <Link 
            to="/login" 
            className="text-sm text-slate-600 hover:text-slate-900 flex items-center justify-center"
            data-testid="back-to-login"
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Volver al inicio de sesión
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default ForgotPassword;
