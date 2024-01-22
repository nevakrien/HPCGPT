/*
 * TinyGPT
 * @author 	: keith@robot9.me
 *
 */
#include <iostream>
#include "Logger.h"
#include "Tokenizer.h"
#include "Model.h"

#include <cassert>
#include <cstdio>

#define GPT2_HPARAMS_PATH "assets/gpt2/hparams.json"
#define GPT2_MODEL_DICT_PATH "assets/gpt2/model_index.json"
#define GPT2_ENCODER "assets/gpt2"

#define MAX_INPUT_LEN 64
#define MAX_GPT_TOKEN 64
#define TOKEN_END_LINE 198

#define INPUT_EXIT "exit\n"

using namespace TinyGPT;

int main() {

  #ifdef TIME_BENCHMARK
  std::cout << "TIME_BENCHMARK is defined." << std::endl;
  #else
  std::cout << "TIME_BENCHMARK is not defined." << std::endl;
  #endif


  GPT2 gpt2;

  // load model
  bool ret = Model::loadModelGPT2(gpt2, GPT2_HPARAMS_PATH, GPT2_MODEL_DICT_PATH);
  if (!ret) {
    LOGE("load GPT2 model failed !");
    return -1;
  }

  assert(MAX_GPT_TOKEN < gpt2.hparams.n_ctx);

  // init tokenizer
  Encoder encoder = Encoder::getEncoder(GPT2_ENCODER);

  
  
  const std::string inputs[2]={"helo world","hi"};
  for(int i=0; i<2;i++){

    
    const std::string inputStr(inputs[i]);
    std::cout<<"INPUT:"<<inputStr<<"\n";
    //std::printf("INPUT:"+inputStr.c_str()+"\n");

    auto tokens = encoder.encode(inputStr);
    auto maxTokens = MAX_GPT_TOKEN - (uint32_t) tokens.size();
    bool skipHeadBlank = true;

    // generate answers
    std::printf("GPT:");
    Model::generate(tokens, gpt2.params, gpt2.hparams.n_head, maxTokens, [&](int32_t token) -> bool {
      if (skipHeadBlank && token == TOKEN_END_LINE) {
        return false;
      }
      skipHeadBlank = false;
      if (token == TOKEN_END_LINE) {
        return true;
      }
      auto outputText = encoder.decode({token});
      std::printf("%s", outputText.c_str());
      std::fflush(stdout);
      return false;
    });
    std::printf("\nINPUT:");
  }

  return 0;
}
