import { cn } from './utils';

describe('cn utility', () => {
  it('should merge classes properly', () => {
    expect(cn('bg-red-500', 'text-white')).toBe('bg-red-500 text-white');
  });

  it('should handle conditional classes', () => {
    expect(cn('bg-red-500', true && 'text-white', false && 'p-4')).toBe('bg-red-500 text-white');
  });

  it('should merge tailwind classes with twMerge', () => {
    expect(cn('p-4 p-8')).toBe('p-8');
    expect(cn('px-2 py-1 p-4')).toBe('p-4');
  });

  it('should handle edge cases: null and undefined', () => {
    expect(cn('bg-red-500', null, undefined, 'text-white')).toBe('bg-red-500 text-white');
  });

  it('should handle edge cases: empty string', () => {
    expect(cn('bg-red-500', '', 'text-white')).toBe('bg-red-500 text-white');
  });

  it('should handle edge cases: arrays and objects', () => {
    expect(cn(['bg-red-500', 'text-white'])).toBe('bg-red-500 text-white');
    expect(cn({ 'bg-red-500': true, 'text-white': false })).toBe('bg-red-500');
  });
});
