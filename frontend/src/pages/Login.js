import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card } from '../components/ui/card';
import { toast } from 'sonner';
import { Lock, Mail, Loader2 } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      toast.success('¡Bienvenido!');
      navigate('/dashboard');
    } else {
      toast.error(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex" data-testid="login-page">
      {/* Left Side - Image */}
      <div 
        className="hidden lg:flex lg:w-1/2 bg-cover bg-center relative"
        style={{ backgroundImage: `url('https://images.unsplash.com/photo-1604636559893-a748bfecfa0e?auto=format&fit=crop&q=80')` }}
      >
        <div className="absolute inset-0 bg-slate-900/60 flex items-center justify-center">
          <div className="text-center px-8">
            <h1 className="text-5xl font-black text-white mb-4" style={{ fontFamily: 'Chivo, sans-serif' }}>
              AssetGuard Pro
            </h1>
            <p className="text-xl text-slate-200 font-medium">
              Control Inteligente de Activos y Mantenimiento
            </p>
          </div>
        </div>
      </div>

      {/* Right Side - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50">
        <Card className="w-full max-w-md p-8 bg-white border border-slate-200 shadow-sm rounded-sm">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Chivo, sans-serif' }}>
              Iniciar Sesión
            </h2>
            <p className="text-slate-600">Accede a tu cuenta para continuar</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
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
                  data-testid="email-input"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="pl-10 bg-white border-slate-200 focus:ring-2 focus:ring-slate-900/10 rounded-sm"
                  placeholder="tu@email.com"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="password" className="text-sm font-bold uppercase tracking-wider text-slate-600">
                Contraseña
              </Label>
              <div className="mt-2 relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
                <Input
                  id="password"
                  type="password"
                  required
                  data-testid="password-input"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="pl-10 bg-white border-slate-200 focus:ring-2 focus:ring-slate-900/10 rounded-sm"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              data-testid="login-button"
              className="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-sm font-medium shadow-sm"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Iniciando sesión...
                </>
              ) : (
                'Iniciar Sesión'
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-600">
              ¿No tienes cuenta?{' '}
              <Link to="/register" className="font-semibold text-slate-900 hover:underline" data-testid="register-link">
                Registrarse
              </Link>
            </p>
            <p className="text-sm text-slate-600 mt-2">
              <Link to="/forgot-password" className="font-semibold text-slate-900 hover:underline" data-testid="forgot-password-link">
                ¿Olvidaste tu contraseña?
              </Link>
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Login;
