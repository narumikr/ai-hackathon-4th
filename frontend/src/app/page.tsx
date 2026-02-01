import { Container } from '@/components/layout';
import { Button, Icon } from '@/components/ui';
import { APP_DESCRIPTION, APP_NAME, BUTTON_LABELS, HOME_CONTENT } from '@/constants';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="bg-gradient-to-b from-primary-50 to-white">
      {/* Hero Section */}
      <section className="py-16 lg:py-24">
        <Container>
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="mb-6 font-bold text-4xl text-neutral-900 lg:text-5xl">{APP_NAME}</h1>
            <p className="mb-8 text-lg text-neutral-600 lg:text-xl">{APP_DESCRIPTION}</p>
            <p className="mb-12 text-base text-neutral-500">{HOME_CONTENT.HERO_SUBTITLE}</p>
            <div className="flex flex-col justify-center gap-4 sm:flex-row">
              <Link href="/travel/new">
                <Button size="lg">{BUTTON_LABELS.CREATE_NEW_TRAVEL}</Button>
              </Link>
              <Link href="/travel">
                <Button variant="secondary" size="lg">
                  {BUTTON_LABELS.VIEW_TRAVEL_LIST}
                </Button>
              </Link>
            </div>
          </div>
        </Container>
      </section>

      {/* Features Section */}
      <section className="bg-white py-16">
        <Container>
          <h2 className="mb-12 text-center font-bold text-3xl text-neutral-900">
            {HOME_CONTENT.SECTION_TITLES.MAIN_FEATURES}
          </h2>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
            {HOME_CONTENT.FEATURES.map(feature => (
              <div
                key={feature.title}
                className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                <h3 className="mb-4 flex items-center gap-3 font-semibold text-neutral-900 text-xl">
                  <Icon name={feature.iconName} size="lg" decorative />
                  {feature.title}
                </h3>
                <p className="text-neutral-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* How to Use Section */}
      <section className="bg-neutral-50 py-16">
        <Container>
          <h2 className="mb-12 text-center font-bold text-3xl text-neutral-900">
            {HOME_CONTENT.SECTION_TITLES.HOW_TO_USE}
          </h2>
          <div className="mx-auto max-w-3xl space-y-8">
            {HOME_CONTENT.STEPS.map((step, index) => (
              <div key={step.title} className="flex gap-4">
                <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-primary-400 font-bold text-lg text-primary-950">
                  {index + 1}
                </div>
                <div>
                  <h3 className="mb-2 font-semibold text-neutral-900 text-xl">{step.title}</h3>
                  <p className="text-neutral-600">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-100 py-16">
        <Container>
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="mb-4 font-bold text-3xl text-neutral-900">
              {HOME_CONTENT.SECTION_TITLES.CTA}
            </h2>
            <p className="mb-8 text-lg text-neutral-600">{HOME_CONTENT.CTA_SUBTITLE}</p>
            <Link href="/travel/new">
              <Button size="lg">{BUTTON_LABELS.START_NOW}</Button>
            </Link>
          </div>
        </Container>
      </section>
    </div>
  );
}
