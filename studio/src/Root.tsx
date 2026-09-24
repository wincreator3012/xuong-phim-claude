import React from 'react';
import {Composition, Folder} from 'remotion';
import {loadFonts} from './fonts';
import {Intro, IntroProps, introDefaults} from './components/Intro';
import {Outro, OutroProps, outroDefaults} from './components/Outro';
import {
  SectionTitle,
  SectionTitleProps,
  sectionTitleDefaults,
} from './components/SectionTitle';
import {
  InfoList,
  InfoListProps,
  infoListDefaults,
  infoListSuggestedSeconds,
} from './components/InfoList';
import {InfoQuote, InfoQuoteProps, infoQuoteDefaults} from './components/InfoQuote';
import {InfoStat, InfoStatProps, infoStatDefaults} from './components/InfoStat';
import {
  InfoSteps,
  InfoStepsProps,
  infoStepsDefaults,
  infoStepsSuggestedSeconds,
} from './components/InfoSteps';
import {
  LowerThird,
  LowerThirdProps,
  lowerThirdDefaults,
} from './components/LowerThird';
import {Benefits, BenefitsProps, benefitsDefaults} from './components/Benefits';
import {YNiem, YNiemProps, yNiemDefaults, yNiemSuggestedSeconds} from './components/YNiem';
import {YCanh, YCanhProps, yCanhDefaults, yCanhSuggestedSeconds} from './components/YCanh';

loadFonts();

export const FPS = 30;
const NGANG = {width: 1920, height: 1080};
const DOC = {width: 1080, height: 1920};

type WithDuration = {durationInSeconds?: number};

const seconds = (s: number) => Math.max(1, Math.round(s * FPS));

// Tính thời lượng từ props; mỗi loại có fallback hợp lý
const durationOf = (props: WithDuration, fallback: number) =>
  seconds(props.durationInSeconds ?? fallback);

export const RemotionRoot: React.FC = () => {
  const both = [
    {suffix: 'ngang', ...NGANG},
    {suffix: 'doc', ...DOC},
  ];

  return (
    <>
      {both.map(({suffix, width, height}) => (
        <Folder key={suffix} name={suffix === 'ngang' ? 'Khung-ngang-16-9' : 'Khung-doc-9-16'}>
          <Composition
            id={`Intro-${suffix}`}
            component={Intro}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(6)}
            defaultProps={introDefaults as IntroProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(props, 6),
            })}
          />
          <Composition
            id={`Outro-${suffix}`}
            component={Outro}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(8)}
            defaultProps={outroDefaults as OutroProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(props, props.qrFile ? 9 : 8),
            })}
          />
          <Composition
            id={`SectionTitle-${suffix}`}
            component={SectionTitle}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(4)}
            defaultProps={sectionTitleDefaults as SectionTitleProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(props, 4),
            })}
          />
          <Composition
            id={`InfoList-${suffix}`}
            component={InfoList}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(8)}
            defaultProps={infoListDefaults as InfoListProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(
                props,
                infoListSuggestedSeconds(props.items ?? [], Boolean(props.title)),
              ),
            })}
          />
          <Composition
            id={`InfoQuote-${suffix}`}
            component={InfoQuote}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(7)}
            defaultProps={infoQuoteDefaults as InfoQuoteProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(props, 7),
            })}
          />
          <Composition
            id={`InfoStat-${suffix}`}
            component={InfoStat}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(6)}
            defaultProps={infoStatDefaults as InfoStatProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(props, 6),
            })}
          />
          <Composition
            id={`InfoSteps-${suffix}`}
            component={InfoSteps}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(8)}
            defaultProps={infoStepsDefaults as InfoStepsProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(
                props,
                infoStepsSuggestedSeconds(props.steps ?? [], Boolean(props.title)),
              ),
            })}
          />
          <Composition
            id={`LowerThird-${suffix}`}
            component={LowerThird}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(5)}
            defaultProps={lowerThirdDefaults as LowerThirdProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(props, 5),
            })}
          />
          <Composition
            id={`Benefits-${suffix}`}
            component={Benefits}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(6)}
            defaultProps={benefitsDefaults as BenefitsProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(props, 6),
            })}
          />
          <Composition
            id={`YNiem-${suffix}`}
            component={YNiem}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(3)}
            defaultProps={yNiemDefaults as YNiemProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(
                props,
                yNiemSuggestedSeconds(props.drawSeconds, props.labelAt),
              ),
            })}
          />
          <Composition
            id={`YCanh-${suffix}`}
            component={YCanh}
            width={width}
            height={height}
            fps={FPS}
            durationInFrames={seconds(4)}
            defaultProps={yCanhDefaults as YCanhProps}
            calculateMetadata={({props}) => ({
              durationInFrames: durationOf(props, yCanhSuggestedSeconds(props.variant)),
            })}
          />
        </Folder>
      ))}
    </>
  );
};
